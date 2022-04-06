function cardLink(card) {
	const mainLink = card.querySelector('.text-link--card')
	const clickableElements = Array.from(card.querySelectorAll('.text-link'))

	clickableElements.forEach((ele) => ele.addEventListener('click', (e) => e.stopPropagation()))

	function handleClick() {
		const noTextSelected = !window.getSelection().toString()

		if (noTextSelected) {
			mainLink.click()
		}
	}

	card.addEventListener('click', handleClick)
}

document.addEventListener('DOMContentLoaded', () => {
	if (document.querySelector('.incident-card--inner')) {
		document.querySelectorAll('.incident-card--inner').forEach((card) => {
			cardLink(card)
		})
	}

	if (document.querySelector('.blog-card--inner')) {
		document.querySelectorAll('.blog-card--inner').forEach((card) => {
			cardLink(card)
		})
	}
})
