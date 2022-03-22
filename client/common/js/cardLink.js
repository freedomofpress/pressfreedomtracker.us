function cardLink(selector) {
	const card = document.querySelector(selector)
	const mainLink = card.querySelector(".text-link--card")
	const clickableElements = Array.from(card.querySelectorAll(".text-link"))

	clickableElements.forEach((ele) =>
		ele.addEventListener("click", (e) => e.stopPropagation())
	)

	function handleClick(event) {
		const noTextSelected = !window.getSelection().toString()

		if (noTextSelected) {
			mainLink.click()
		}
	}

	card.addEventListener("click", handleClick)
}

document.addEventListener('DOMContentLoaded', () => {
	if (document.querySelector(".incident-card--inner")) {
		cardLink(".incident-card--inner")
	}

	if (document.querySelector(".blog-card--inner")) {
		cardLink(".blog-card--inner")
	}
})
