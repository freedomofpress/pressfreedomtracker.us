const filterSidebar = document.querySelector('#database-filters')
const filterToggle = document.querySelector('.mobile-filter-toggle')

filterToggle.addEventListener('click', () => {
	if (filterSidebar.dataset.visible === 'false') {
		document.body.classList.add('overflow-hidden')
		filterSidebar.dataset.visible = 'true'
		filterToggle.setAttribute('aria-expanded', 'true')
	} else if (filterSidebar.dataset.visible === 'true') {
		document.body.classList.remove('overflow-hidden')
		filterSidebar.dataset.visible = 'false'
		filterToggle.setAttribute('aria-expanded', 'false')
	}
})
