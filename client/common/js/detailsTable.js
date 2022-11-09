import {showMoreTable} from './utils'

document.querySelectorAll('.list-table-toggle-btn').forEach((button) => {
	const listId = button.getAttribute('aria-controls')
	const list = document.getElementById(listId)
	const count = list.querySelector('ul').children.length
	if (count < 8) {
		// our list is not long enough to collapse, so remove the
		// button only.
		button.setAttribute('data-visible', 'false')
	} else {
		button.setAttribute('aria-expanded', 'false')
		list.classList.add('list-table--collapsed')
		button.addEventListener('click', (e) => {
			if (e.target.getAttribute('aria-expanded') === 'false') {
				e.target.innerText = 'Show Less'
				e.target.setAttribute('aria-expanded', 'true')
				list.classList.remove('list-table--collapsed')
				list.classList.add('list-table--expanded')
			} else {
				e.target.innerText = 'Show All'
				e.target.setAttribute('aria-expanded', 'false')
				list.classList.add('list-table--collapsed')
				list.classList.remove('list-table--expanded')
			}
		})
	}
})

if (document.querySelector('#details-toggle-btn')) {
	const detailsBtn = document.querySelector('#details-toggle-btn')
	const detailsDiv = document.querySelector('#incident-details')

	detailsDiv.dataset.visible = 'false'
	detailsBtn.setAttribute('aria-expanded', 'false')
	detailsBtn.classList.add('has-js')

	detailsBtn.addEventListener('click', () => {
		if (detailsDiv.dataset.visible === 'false') {
			detailsDiv.dataset.visible = 'true'
			detailsBtn.setAttribute('aria-expanded', 'true')
			detailsBtn.innerText = 'Show Less'
		} else if (detailsDiv.dataset.visible === 'true') {
			detailsDiv.dataset.visible = 'false'
			detailsBtn.setAttribute('aria-expanded', 'false')
			detailsBtn.innerText = 'Show More'
		}
	})
}

document.querySelectorAll('.incident-database-card__details-toggle').forEach((button) => {
	button.addEventListener('click', showMoreTable)
})
