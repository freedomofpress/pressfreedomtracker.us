function collapsibleCard(card) {
	function toggleCard() {
		if (card.classList.contains('closed')) {
			card.classList.remove('closed')
			card.classList.add('open')
			const buttonTextEl = card.querySelector('.incident-card-collapsible__toggle-button-text')
			if (buttonTextEl) buttonTextEl.innerText = 'Show Less'
		} else {
			card.classList.remove('open')
			card.classList.add('closed')
			const buttonTextEl = card.querySelector('.incident-card-collapsible__toggle-button-text')
			if (buttonTextEl) buttonTextEl.innerText = 'Show More'
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
