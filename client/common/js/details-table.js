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
	button.addEventListener('click', (e) => {
		const isVisible = Boolean(e.target.dataset.visible === 'true')
		const newVisible = !isVisible
		const newText = newVisible ? 'Show Less' : 'Show More'
		e.target.innerText = newText
		e.target.dataset.visible = newVisible.toString()
		e.target.setAttribute('aria-expanded', newVisible.toString())
		e.target.getAttribute('aria-controls').split(' ').forEach((id) => {
			document.getElementById(id).dataset.visible = newVisible.toString()
		})
	})
})
