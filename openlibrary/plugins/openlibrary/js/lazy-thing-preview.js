// @ts-check
import debounce from 'lodash/debounce';

/**
 * Responds to HTML like:
 * ```html
 *  <div
 *      class="lazy-thing-preview"
 *      data-key="/works/OL123W"
 *      data-render-fn="$render_fn_name"
 * ></div>
 * ```
 *
 * And then calls `$render_fn_name` with the response from search engine.
 * Bundles/dedupes requests throughout the page and does other smart things.
 * Someday: Only load if in viewport.
 * Currently only works with works/editions.
 */
export class LazyThingPreview {
    constructor() {
        /** @type {Array<{key: string, render_fn: Function}>} */
        this.queue = [];
        /** @type {Object<string, object>} */
        this.cache = {};

        this.renderDebounced = debounce(this.render.bind(this), 100);
    }

    init() {
        $('.lazy-thing-preview').each((i, el) => {
            this.push({
                key: el.dataset.key,
                render_fn_name: el.dataset.renderFn,
            });
        });
    }

    /**
     * @param {{key: string, render_fn_name: string}} arg0
     */
    push({key, render_fn_name}) {
        const render_fn = window[render_fn_name];
        if (this.cache[key]) {
            this.renderKey(key, render_fn, this.cache[key]);
        } else {
            this.queue.push({key, render_fn});
            this.renderDebounced();
        }
    }

    /**
     * @param {string} key
     * @param {Function} render_fn
     * @param {object} book
     */
    renderKey(key, render_fn, book) {
        const $el = $(`.lazy-thing-preview[data-key="${key}"]`);
        $el.html(render_fn(book));
    }

    /**
     * @param {string[]} keys
     * @returns {Promise<object[]>}
     */
    async getThings(keys) {
        const workKeys = keys.filter(key => key.startsWith('/works/'));
        const editionKeys = keys.filter(key => key.startsWith('/books/'));
        const authorKeys = keys.filter(key => key.startsWith('/authors/'));
        const fields = 'key,type,cover_i,first_publish_year,author_name,title,subtitle,edition_count,editions';
        let docs = [];
        if (workKeys.length) {
            const resp = await fetch(`/search.json?${new URLSearchParams({
                q: `key:(${workKeys.join(' OR ')})`,
                fields,
            })}`).then(r => r.json());
            docs = docs.concat(resp.docs);
        }
        if (editionKeys.length) {
            const resp = await fetch(`/search.json?${new URLSearchParams({
                q: `edition_key:(${editionKeys
                    .map(key => key.split('/').pop())
                    .join(' OR ')})`,
                fields,
            })}`).then(r => r.json());
            docs = docs.concat(resp.docs);
        }
        if (authorKeys.length) {
            const resp = await fetch(`/search/authors.json?${new URLSearchParams({
                q: `key:(${authorKeys.join(' OR ')})`,
                fields: 'key,type,name,top_work,top_subjects,birth_date,death_date',
            })}`).then(r => r.json());
            for (const doc of resp.docs) {
                // This API returns keys without the /authors/ prefix 😭
                doc.key = `/authors/${doc.key}`;
            }
            docs = docs.concat(resp.docs);
        }

        return docs;
    }

    async render() {
        const keys = this.queue.map(({key}) => key);
        const things = await this.getThings(keys);
        for (const thing of things) {
            this.cache[thing.key] = thing;
            if (thing.type === 'work') {
                const book = thing;
                book.full_title = book.subtitle ? `${book.title}: ${book.subtitle}` : book.title;
                if (book.editions.docs.length) {
                    const ed = book.editions.docs[0];
                    ed.full_title = ed.subtitle ? `${ed.title}: ${ed.subtitle}` : ed.title;
                    ed.author_name = book.author_name;
                    ed.edition_count = book.edition_count;
                    this.cache[ed.key] = ed;
                }
            }
        }

        const missingKeys = keys.filter(key => !this.cache[key]);
        // eslint-disable-next-line no-console
        console.warn('Books missing from cache', missingKeys);

        for (const {key, render_fn} of this.queue) {
            this.renderKey(key, render_fn, this.cache[key]);
        }
        this.queue = [];
    }
}