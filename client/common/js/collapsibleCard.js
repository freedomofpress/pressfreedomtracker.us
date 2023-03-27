function collapsibleCard(card) {
	function toggleCard() {
		if (card.classList.contains('closed')) {
			card.classList.remove('closed')
			card.classList.add('open')
			card.querySelectorAll('.incident-card-collapsible__toggle-button-text')
				// eslint-disable-next-line no-param-reassign
				.forEach((buttonText) => { buttonText.innerText = 'Show Less' })
		} else {
			card.classList.remove('open')
			card.classList.add('closed')
			card.querySelectorAll('.incident-card-collapsible__toggle-button-text')
				// eslint-disable-next-line no-param-reassign
				.forEach((buttonText) => { buttonText.innerText = 'Show More' })
		}
	}

	// Initialize card to closed if js is enabled
	toggleCard()

	card.querySelectorAll('.incident-card-collapsible__toggle-button').forEach(
		(ele) => ele.addEventListener('click', toggleCard),
	)
}

document.addEventListener('DOMContentLoaded', () => {
	document.querySelectorAll('.incident-card-collapsible').forEach((card) => {
		collapsibleCard(card)
	})
})
