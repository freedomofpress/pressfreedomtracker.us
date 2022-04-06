function tableRowLink(tableRow) {
	const mainLink = tableRow.querySelector('.anim-table-mainlink')
	const mainLinkText = mainLink.innerText
	const clickableElements = Array.from(tableRow.querySelectorAll('.text-link'))

	clickableElements.forEach((ele) => ele.addEventListener('click', (e) => e.stopPropagation()))

	function handleClick() {
		const noTextSelected = !window.getSelection().toString()

		if (noTextSelected) {
			mainLink.click()
		}
	}

	function updateLinkText(event) {
		if (event.type === 'mouseover') {
			mainLink.innerHTML = '&rarr;'
			mainLink.classList.add('anim-table-mainLink--hovered')
		} else if (event.type === 'mouseout') {
			mainLink.innerText = mainLinkText
			mainLink.classList.remove('anim-table-mainLink--hovered')
		}
	}

	tableRow.addEventListener('mouseover', updateLinkText)
	tableRow.addEventListener('mouseout', updateLinkText)
	tableRow.addEventListener('click', handleClick)
}

document.addEventListener('DOMContentLoaded', () => {
	if (document.querySelector('.anim-table-row')) {
		document.querySelectorAll('.anim-table-row').forEach((tableRow) => {
			tableRowLink(tableRow)
		})
	}
})
