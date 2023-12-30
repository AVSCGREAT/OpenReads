"""Helper functions used by the List model.
"""
from functools import cached_property

import web
import logging

from infogami import config
from infogami.infobase import client, common
from infogami.utils import stats

from openlibrary.core import helpers as h
from openlibrary.core import cache
from openlibrary.core.models import Image, Thing
from openlibrary.plugins.upstream.models import Changeset

from openlibrary.plugins.worksearch.search import get_solr
from openlibrary.plugins.worksearch.subjects import get_subject
import contextlib

logger = logging.getLogger("openlibrary.lists.model")


class List(Thing):
    """Class to represent /type/list objects in OL.

    List contains the following properties:

        * name - name of the list
        * description - detailed description of the list (markdown)
        * members - members of the list. Either references or subject strings.
        * cover - id of the book cover. Picked from one of its editions.
        * tags - list of tags to describe this list.
    """

    def url(self, suffix="", **params):
        return self.get_url(suffix, **params)

    def get_url_suffix(self):
        return self.name or "unnamed"

    def get_owner(self):
        if match := web.re_compile(r"(/people/[^/]+)/lists/OL\d+L").match(self.key):
            key = match.group(1)
            return self._site.get(key)

    def get_cover(self):
        """Returns a cover object."""
        return self.cover and Image(self._site, "b", self.cover)

    def get_tags(self):
        """Returns tags as objects.

        Each tag object will contain name and url fields.
        """
        return [web.storage(name=t, url=self.key + "/tags/" + t) for t in self.tags]

    def _get_subjects(self):
        """Returns list of subjects inferred from the seeds.
        Each item in the list will be a storage object with title and url.
        """
        # sample subjects
        return [
            web.storage(title="Cheese", url="/subjects/cheese"),
            web.storage(title="San Francisco", url="/subjects/place:san_francisco"),
        ]

    def add_seed(self, seed):
        """Adds a new seed to this list.

        seed can be:
            - author, edition or work object
            - {"key": "..."} for author, edition or work objects
            - subject strings.
        """
        if isinstance(seed, Thing):
            seed = {"key": seed.key}

        index = self._index_of_seed(seed)
        if index >= 0:
            return False
        else:
            self.seeds = self.seeds or []
            self.seeds.append(seed)
            return True

    def remove_seed(self, seed):
        """Removes a seed for the list."""
        if isinstance(seed, Thing):
            seed = {"key": seed.key}

        if (index := self._index_of_seed(seed)) >= 0:
            self.seeds.pop(index)
            return True
        else:
            return False

    def _index_of_seed(self, seed):
        for i, s in enumerate(self.seeds):
            if isinstance(s, Thing):
                s = {"key": s.key}
            if s == seed:
                return i
        return -1

    def __repr__(self):
        return f"<List: {self.key} ({self.name!r})>"

    def _get_rawseeds(self):
        def process(seed):
            if isinstance(seed, str):
                return seed
            else:
                return seed.key

        return [process(seed) for seed in self.seeds]

    @cached_property
    def last_update(self):
        last_updates = [seed.last_update for seed in self.get_seeds()]
        last_updates = [x for x in last_updates if x]
        if last_updates:
            return max(last_updates)
        else:
            return None

    @property
    def seed_count(self):
        return len(self.seeds)

    def preview(self):
        """Return data to preview this list.

        Used in the API.
        """
        return {
            "url": self.key,
            "full_url": self.url(),
            "name": self.name or "",
            "seed_count": self.seed_count,
            "last_update": self.last_update and self.last_update.isoformat() or None,
        }

    def get_book_keys(self, offset=0, limit=50):
        offset = offset or 0
        return list(
            {
                (seed.works[0].key if seed.works else seed.key)
                for seed in self.seeds
                if seed.key.startswith(('/books', '/works'))
            }
        )[offset : offset + limit]

    def get_editions(self, limit=50, offset=0, _raw=False):
        """Returns the editions objects belonged to this list ordered by last_modified.

        When _raw=True, the edtion dicts are returned instead of edtion objects.
        """
        edition_keys = {
            seed.key for seed in self.seeds if seed and seed.type.key == '/type/edition'
        }

        editions = web.ctx.site.get_many(list(edition_keys))

        return {
            "count": len(editions),
            "offset": offset,
            "limit": limit,
            "editions": editions,
        }
        # TODO
        # We should be able to get the editions from solr and return that.
        # Might be an issue of the total number of editions is too big, but
        # that isn't the case for most lists.

    def get_all_editions(self):
        """Returns all the editions of this list in arbitrary order.

        The return value is an iterator over all the editions. Each entry is a dictionary.
        (Compare the difference with get_editions.)

        This works even for lists with too many seeds as it doesn't try to
        return editions in the order of last-modified.
        """
        edition_keys = {
            seed.key for seed in self.seeds if seed and seed.type.key == '/type/edition'
        }

        def get_query_term(seed):
            if seed.type.key == "/type/work":
                return "key:%s" % seed.key.split("/")[-1]
            if seed.type.key == "/type/author":
                return "author_key:%s" % seed.key.split("/")[-1]

        query_terms = [get_query_term(seed) for seed in self.seeds]
        query_terms = [q for q in query_terms if q]  # drop Nones
        edition_keys = set(self._get_edition_keys_from_solr(query_terms))

        # Add all editions
        edition_keys.update(
            seed.key for seed in self.seeds if seed and seed.type.key == '/type/edition'
        )

        return [doc.dict() for doc in web.ctx.site.get_many(list(edition_keys))]

    def _get_edition_keys_from_solr(self, query_terms):
        if not query_terms:
            return
        q = " OR ".join(query_terms)
        solr = get_solr()
        result = solr.select(q, fields=["edition_key"], rows=10000)
        for doc in result['docs']:
            if 'edition_key' not in doc:
                continue
            for k in doc['edition_key']:
                yield "/books/" + k

    def get_export_list(self) -> dict[str, list]:
        """Returns all the editions, works and authors of this list in arbitrary order.

        The return value is an iterator over all the entries. Each entry is a dictionary.

        This works even for lists with too many seeds as it doesn't try to
        return entries in the order of last-modified.
        """

        # Separate by type each of the keys
        edition_keys = {
            seed.key for seed in self.seeds if seed and seed.type.key == '/type/edition'  # type: ignore[attr-defined]
        }
        work_keys = {
            "/works/%s" % seed.key.split("/")[-1] for seed in self.seeds if seed and seed.type.key == '/type/work'  # type: ignore[attr-defined]
        }
        author_keys = {
            "/authors/%s" % seed.key.split("/")[-1] for seed in self.seeds if seed and seed.type.key == '/type/author'  # type: ignore[attr-defined]
        }

        # Create the return dictionary
        export_list = {}
        if edition_keys:
            export_list["editions"] = [
                doc.dict() for doc in web.ctx.site.get_many(list(edition_keys))
            ]
        if work_keys:
            export_list["works"] = [
                doc.dict() for doc in web.ctx.site.get_many(list(work_keys))
            ]
        if author_keys:
            export_list["authors"] = [
                doc.dict() for doc in web.ctx.site.get_many(list(author_keys))
            ]

        return export_list

    def _preload(self, keys):
        keys = list(set(keys))
        return self._site.get_many(keys)

    def preload_works(self, editions):
        return self._preload(w.key for e in editions for w in e.get('works', []))

    def preload_authors(self, editions):
        works = self.preload_works(editions)
        return self._preload(
            a.author.key for w in works for a in w.get("authors", []) if "author" in a
        )

    def load_changesets(self, editions):
        """Adds "recent_changeset" to each edition.

        The recent_changeset will be of the form:
            {
                "id": "...",
                "author": {
                    "key": "..",
                    "displayname", "..."
                },
                "timestamp": "...",
                "ip": "...",
                "comment": "..."
            }
        """
        for e in editions:
            if "recent_changeset" not in e:
                with contextlib.suppress(IndexError):
                    e['recent_changeset'] = self._site.recentchanges(
                        {"key": e.key, "limit": 1}
                    )[0]

    def _get_solr_query_for_subjects(self):
        terms = [seed.get_solr_query_term() for seed in self.get_seeds()]
        return " OR ".join(t for t in terms if t)

    def _get_all_subjects(self):
        solr = get_solr()
        q = self._get_solr_query_for_subjects()

        # Solr has a maxBooleanClauses constraint there too many seeds, the
        if len(self.seeds) > 500:
            logger.warning(
                "More than 500 seeds. skipping solr query for finding subjects."
            )
            return []

        facet_names = ['subject_facet', 'place_facet', 'person_facet', 'time_facet']
        try:
            result = solr.select(
                q, fields=[], facets=facet_names, facet_limit=20, facet_mincount=1
            )
        except OSError:
            logger.error(
                "Error in finding subjects of list %s", self.key, exc_info=True
            )
            return []

        def get_subject_prefix(facet_name):
            name = facet_name.replace("_facet", "")
            if name == 'subject':
                return ''
            else:
                return name + ":"

        def process_subject(facet_name, title, count):
            prefix = get_subject_prefix(facet_name)
            key = prefix + title.lower().replace(" ", "_")
            url = "/subjects/" + key
            return web.storage(
                {"title": title, "name": title, "count": count, "key": key, "url": url}
            )

        def process_all():
            facets = result['facets']
            for k in facet_names:
                for f in facets.get(k, []):
                    yield process_subject(f.name, f.value, f.count)

        return sorted(process_all(), reverse=True, key=lambda s: s["count"])

    def get_subjects(self, limit=20):
        def get_subject_type(s):
            if s.url.startswith("/subjects/place:"):
                return "places"
            elif s.url.startswith("/subjects/person:"):
                return "people"
            elif s.url.startswith("/subjects/time:"):
                return "times"
            else:
                return "subjects"

        d = web.storage(subjects=[], places=[], people=[], times=[])

        for s in self._get_all_subjects():
            kind = get_subject_type(s)
            if len(d[kind]) < limit:
                d[kind].append(s)
        return d

    def get_seeds(self, sort=False, resolve_redirects=False):
        seeds = []
        for s in self.seeds:
            seed = Seed(self, s)
            max_checks = 10
            while resolve_redirects and seed.type == 'redirect' and max_checks:
                seed = Seed(self, web.ctx.site.get(seed.document.location))
                max_checks -= 1
            seeds.append(seed)

        if sort:
            seeds = h.safesort(seeds, reverse=True, key=lambda seed: seed.last_update)

        return seeds

    def get_seed(self, seed):
        if isinstance(seed, dict):
            seed = seed['key']
        return Seed(self, seed)

    def has_seed(self, seed):
        if isinstance(seed, dict):
            seed = seed['key']
        return seed in self._get_rawseeds()

    # cache the default_cover_id for 60 seconds
    @cache.memoize(
        "memcache", key=lambda self: ("d" + self.key, "default-cover-id"), expires=60
    )
    def _get_default_cover_id(self):
        for s in self.get_seeds():
            cover = s.get_cover()
            if cover:
                return cover.id

    def get_default_cover(self):
        from openlibrary.core.models import Image

        cover_id = self._get_default_cover_id()
        return Image(self._site, 'b', cover_id)

    @cache.memoize(
             "memcache",
             key = lambda self: 'core.patron_lists.%s.%s' % (self.get_owner().name.replace(' ', '_'), self.name.replace(' ', '_')),
             expires = 60
             )
    def get_patron_showcase(self, limit = 3):
       return self._get_uncached_patron_showcase(limit = limit)
    
    def _get_uncached_patron_showcase(self, limit = 3):
        title = self.name or "Unnamed List"
        n_covers = []
        seeds = self.get_seeds()
        for seed in seeds[:limit]:
            n_covers.append(seed.get_cover())
        last_modified = self.last_update
        return {'title': title, 'count': self.seed_count, 'covers': n_covers, 'last_mod': last_modified.isoformat(sep = ' ', timespec="minutes")}

class Seed:
    """Seed of a list.

    Attributes:
        * last_update
        * type - "edition", "work" or "subject"
        * document - reference to the edition/work document
        * title
        * url
        * cover
    """

    def __init__(self, list, value: web.storage | str):
        self._list = list
        self._type = None

        self.value = value
        if isinstance(value, str):
            self.key = value
            self._type = "subject"
        else:
            self.key = value.key

    @cached_property
    def document(self):
        if isinstance(self.value, str):
            return get_subject(self.get_subject_url(self.value))
        else:
            return self.value

    def get_solr_query_term(self):
        if self.type == 'subject':
            typ, value = self.key.split(":", 1)
            # escaping value as it can have special chars like : etc.
            value = get_solr().escape(value)
            return f"{typ}_key:{value}"
        else:
            doc_basekey = self.document.key.split("/")[-1]
            if self.type == 'edition':
                return f"edition_key:{doc_basekey}"
            elif self.type == 'work':
                return f'key:/works/{doc_basekey}'
            elif self.type == 'author':
                return f"author_key:{doc_basekey}"
            else:
                logger.warning(
                    f"Cannot get solr query term for seed type {self.type}",
                    extra={'list': self._list.key, 'seed': self.key},
                )
                return None

    @cached_property
    def type(self) -> str:
        if self._type:
            return self._type
        key = self.document.type.key
        if key in ("/type/author", "/type/edition", "/type/redirect", "/type/work"):
            return key.split("/")[-1]
        return "unknown"

    @property
    def title(self):
        if self.type in ("work", "edition"):
            return self.document.title or self.key
        elif self.type == "author":
            return self.document.name or self.key
        elif self.type == "subject":
            return self.key.replace("_", " ")
        else:
            return self.key

    @property
    def url(self):
        if self.document:
            return self.document.url()
        else:
            if self.key.startswith("subject:"):
                return "/subjects/" + web.lstrips(self.key, "subject:")
            else:
                return "/subjects/" + self.key

    def get_subject_url(self, subject):
        if subject.startswith("subject:"):
            return "/subjects/" + web.lstrips(subject, "subject:")
        else:
            return "/subjects/" + subject

    def get_cover(self):
        if self.type in ['work', 'edition']:
            return self.document.get_cover()
        elif self.type == 'author':
            return self.document.get_photo()
        elif self.type == 'subject':
            return self.document.get_default_cover()
        else:
            return None

    @cached_property
    def last_update(self):
        return self.document.get('last_modified')

    def dict(self):
        if self.type == "subject":
            url = self.url
            full_url = self.url
        else:
            url = self.key
            full_url = self.url

        d = {
            "url": url,
            "full_url": full_url,
            "type": self.type,
            "title": self.title,
            "last_update": self.last_update and self.last_update.isoformat() or None,
        }
        if cover := self.get_cover():
            d['picture'] = {"url": cover.url("S")}
        return d

    def __repr__(self):
        return f"<seed: {self.type} {self.key}>"

    __str__ = __repr__


class ListChangeset(Changeset):
    def get_added_seed(self):
        added = self.data.get("add")
        if added and len(added) == 1:
            return self.get_seed(added[0])

    def get_removed_seed(self):
        removed = self.data.get("remove")
        if removed and len(removed) == 1:
            return self.get_seed(removed[0])

    def get_list(self):
        return self.get_changes()[0]

    def get_seed(self, seed):
        """Returns the seed object."""
        if isinstance(seed, dict):
            seed = self._site.get(seed['key'])
        return Seed(self.get_list(), seed)


def register_models():
    client.register_thing_class('/type/list', List)
    client.register_changeset_class('lists', ListChangeset)
