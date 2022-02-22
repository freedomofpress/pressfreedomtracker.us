document.querySelectorAll('.incident-database-card__details-toggle').forEach(button => {
	button.addEventListener('click', (e) => {
		let isVisible = Boolean(e.target.dataset.visible === 'true')
		let newVisible = !isVisible
		let newText = newVisible ? "Show Less" : "Show More"
		e.target.innerText = newText
		e.target.dataset.visible = newVisible.toString()
		e.target.setAttribute('aria-expanded', newVisible.toString())
		e.target.getAttribute('aria-controls').split(' ').forEach(id => {
			document.getElementById(id).dataset.visible = newVisible.toString()
		})
	})
})
