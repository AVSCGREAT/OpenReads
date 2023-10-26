"""
The purpose of this file is to:
1. Interact with the Wikidata API
2. Store the results
3. Make the results easy to access from other files
"""
import requests
import web
import dataclasses
from dataclasses import dataclass
from openlibrary.core.helpers import days_since

from datetime import datetime
import json
from openlibrary.core import db

WIKIDATA_CACHE_TTL_DAYS = 30


@dataclass
class WikidataEntity:
    """
    This is the model of the api response from WikiData plus the updated field
    https://www.wikidata.org/wiki/Wikidata:REST_API
    """

    id: str
    type: str
    labels: dict
    descriptions: dict
    aliases: dict
    statements: dict
    sitelinks: dict
    updated: datetime  # This is when we fetched the data, not when the entity was changed in Wikidata

    def description(self, language: str = 'en') -> str | None:
        """If a description isn't available in the requested language default to English"""
        return self.descriptions.get(language) or self.descriptions.get('en')

    @classmethod
    def from_db_query(cls, db_response: web.utils.Storage):
        response = db_response.data
        return cls(
            id=response['id'],
            type=response['type'],
            labels=response['labels'],
            descriptions=response['descriptions'],
            aliases=response['aliases'],
            statements=response['statements'],
            sitelinks=response['sitelinks'],
            updated=db_response['updated'],
        )

    @classmethod
    def from_web(cls, response: dict):
        return cls(
            id=response['id'],
            type=response['type'],
            labels=response['labels'],
            descriptions=response['descriptions'],
            aliases=response['aliases'],
            statements=response['statements'],
            sitelinks=response['sitelinks'],
            updated=datetime.now(),
        )

    def as_api_response_str(self) -> str:
        """
        Transforms the dataclass a JSON string like we get from the Wikidata API.
        This is used for staring the json in the database.
        """
        self_dict = dataclasses.asdict(self)
        # remove the updated field because it's not part of the API response and is stored in its own column
        self_dict.pop('updated')
        return json.dumps(self_dict)


def get_wikidata_entity(QID: str, use_cache: bool = True) -> WikidataEntity | None:
    """
    This only supports QIDs, if we want to support PIDs we need to use different endpoints
    ttl (time to live) inspired by the cachetools api https://cachetools.readthedocs.io/en/latest/#cachetools.TTLCache
    """

    entity = _get_from_cache(QID)
    if entity and use_cache and days_since(entity.updated) < WIKIDATA_CACHE_TTL_DAYS:
        return entity
    else:
        return _get_from_web(QID)


def _get_from_web(id: str) -> WikidataEntity | None:
    response = requests.get(
        f'https://www.wikidata.org/w/rest.php/wikibase/v0/entities/items/{id}'
    )
    if response.status_code == 200:
        entity = WikidataEntity.from_web(response.json())
        _add_to_cache(entity)
        return entity
    else:
        return None
    # TODO: What should we do in non-200 cases?
    # They're documented here https://doc.wikimedia.org/Wikibase/master/js/rest-api/


def _get_from_cache_by_ids(ids: list[str]) -> list[WikidataEntity]:
    response = list(
        db.get_db().query(
            'select * from wikidata where id IN ($ids)',
            vars={'ids': ids},
        )
    )
    return [WikidataEntity.from_db_query(r) for r in response]


def _get_from_cache(id: str) -> WikidataEntity | None:
    """
    The cache is OpenLibrary's Postgres instead of calling the Wikidata API
    """
    if len(result := _get_from_cache_by_ids([id])) > 0:
        return result[0]
    return None


def _add_to_cache(entity: WikidataEntity) -> None:
    # TODO: after we upgrade to postgres 9.5+ we should use upsert here
    oldb = db.get_db()
    json_data = entity.as_api_response_str()

    if _get_from_cache(entity.id):
        return oldb.update(
            "wikidata",
            where="id=$id",
            vars={'id': entity.id},
            data=json_data,
            updated=datetime.now(),
        )
    else:
        # We don't provide the updated column on insert because postgres defaults to the current time
        return oldb.insert("wikidata", id=entity.id, data=json_data)
