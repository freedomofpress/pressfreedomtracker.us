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
