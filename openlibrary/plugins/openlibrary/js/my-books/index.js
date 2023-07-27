import CreateListForm from './CreateListForm'
import MyBooksDropper from './MyBooksDropper'
import myBooksStore from './store'

export function initMyBooksDroppers(dropperElements) {
    const form = document.querySelector('#create-list-form')
    const createListForm = new CreateListForm(form)
    createListForm.initialize()

    const droppers = []
    for (const dropper of dropperElements) {
        const myBooksDropper = new MyBooksDropper(dropper)
        myBooksDropper.initialize()

        droppers.push(myBooksDropper)
    }

    // Get user key from first Dropper and add to store:
    const userKey = droppers[0].readingLists.userKey
    myBooksStore.set('USER_KEY', userKey)

    myBooksStore.set('DROPPERS', droppers)
}
