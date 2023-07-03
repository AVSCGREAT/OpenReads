/**
 * Defines functionality related to Open Library's My Books dropper components.
 * @module my-books/MyBooksDropper
 */
import ReadDateComponents from './ReadDateComponents'
import ReadingLists from './ReadingLists'
import ReadingLogForms from './ReadingLogForms'
import { fetchPartials } from '../lists/ListService'

/**
 * Represents a single My Books dropper.  Hydrates droppers on instantiation.
 *
 * @class
 */
export default class MyBooksDropper {
    /**
     * Creates references to the given dropper's reading log forms, read date affordances, and
     * list affordances.
     *
     * @param {HTMLElement} dropper
     */
    constructor(dropper) {
        /**
         * Reference to the dropper itself.
         * @param {HTMLElement}
         */
        this.dropper = dropper

        /**
         * References this dropper's read date prompt and display.
         * @param {ReadDateComponents}
         */
        this.readDateComponents = new ReadDateComponents(dropper)

        /**
         * References this dropper's reading log buttons.
         * @param {ReadingLogForms}
         */
        this.readingLogForms = new ReadingLogForms(dropper, this.readDateComponents)
        this.readingLogForms.initialize()

        /**
         * Reference to this dropper's list content.
         * @param {ReadingLists}
         */
        this.readingLists = new ReadingLists(dropper)
        this.readingLists.initialize()
    }

    initialize() {
        this.loadLists()
    }

    /**
     * Replaces loading indicators with HTML fetched from the server.
     */
    loadLists() {
        const dropperListPlaceholder = this.dropper.querySelector('.list-loading-indicator')

        // Already lists showcase --- assuming one per page
        const listDisplayPlaceholder = document.querySelector('.list-overview-loading-indicator')

        const loadingIndicators = dropperListPlaceholder ? [dropperListPlaceholder.querySelector('.loading-ellipsis')] : []
        if (listDisplayPlaceholder) {
            loadingIndicators.push(listDisplayPlaceholder.querySelector('.loading-ellipsis'))
        }
        const intervalId = this.initLoadingAnimation(loadingIndicators)

        let key
        if (dropperListPlaceholder) {  // Not rendered for logged-out patrons
            if (dropperListPlaceholder.dataset.editionKey) {
                key = dropperListPlaceholder.dataset.editionKey
            } else if (dropperListPlaceholder.dataset.workKey) {
                key = dropperListPlaceholder.dataset.workKey
            }
        }

        if (key) {
            fetchPartials(key, (data) => {
                clearInterval(intervalId)
                this.replaceLoadingIndicators(dropperListPlaceholder, listDisplayPlaceholder, JSON.parse(data))
            })
        } else {
            this.removeChildren(dropperListPlaceholder, listDisplayPlaceholder)
        }
    }

    /**
     * Creates loading animation for list affordances.
     *
     * @param {Array<HTMLElement>} loadingIndicators
     * @returns {NodeJS.Timer}
     */
    initLoadingAnimation(loadingIndicators) {
        let count = 0
        const intervalId = setInterval(function() {
            let ellipsis = ''
            for (let i = 0; i < count % 4; ++i) {
                ellipsis += '.'
            }
            for (const elem of loadingIndicators) {
                elem.innerText = ellipsis
            }
            ++count
        }, 1500)

        return intervalId
    }

    /**
     * Object returned by the list partials endpoint.
     *
     * @typedef {Object} ListPartials
     * @property {string} dropper HTML string for dropdown list content
     * @property {string} active HTML string for patron's active lists
     */
    /**
     * Replaces list loading indicators with the given partially rendered HTML.
     *
     * @param {HTMLElement} dropperListsPlaceholder Loading indicator found inside of the dropdown content
     * @param {HTMLElement} activeListsPlaceholder Loading indicator for patron's active lists
     * @param {ListPartials} partials
     */
    replaceLoadingIndicators(dropperListsPlaceholder, activeListsPlaceholder, partials) {
        const dropperParent = dropperListsPlaceholder ? dropperListsPlaceholder.parentElement : null
        const activeListsParent = activeListsPlaceholder ? activeListsPlaceholder.parentElement : null

        if (dropperParent) {
            this.removeChildren(dropperParent)
            dropperParent.insertAdjacentHTML('afterbegin', partials['dropper'])

            const anchors = this.dropper.querySelectorAll('.add-to-list')
            this.readingLists.initAddToListAnchors(anchors)
        }

        if (activeListsParent) {
            this.removeChildren(activeListsParent)
            activeListsParent.insertAdjacentHTML('afterbegin', partials['active'])
            const actionableListItems = activeListsParent.querySelectorAll('.actionable-item')
            this.readingLists.registerListItems(actionableListItems)
        }
    }

    /**
     * Removes children of each given element.
     *
     * @param  {Array<HTMLElement>} elements
     */
    removeChildren(...elements) {
        for (const elem of elements) {
            if (elem) {
                while (elem.firstChild) {
                    elem.removeChild(elem.firstChild)
                }
            }
        }
    }
}
