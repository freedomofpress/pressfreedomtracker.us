// https://remysharp.com/2010/07/21/throttling-function-calls
export function throttle(fn, _threshhold, scope, ...args) {
	let last
	let deferTimer
	const threshhold = _threshhold || 250
	return () => {
		const context = scope || this
		const now = +new Date()
		if (last && now < last + threshhold) {
			// hold on to it
			clearTimeout(deferTimer)
			deferTimer = setTimeout(() => {
				last = now
				fn.apply(context, args)
			}, threshhold)
		} else {
			last = now
			fn.apply(context, args)
		}
	}
}

export function isElementVisible(elm) {
	if (!elm) {
		return false
	}
	const height = window.innerHeight
	const rect = elm.getBoundingClientRect()
	const threshold = (rect.top + rect.bottom) * 0.75
	return threshold < height
}

export function showMoreTable(e) {
	const isVisible = Boolean(e.target.dataset.visible === 'true')
	const newVisible = !isVisible
	const newText = newVisible ? 'Show Less' : 'Show More'
	e.target.innerText = newText
	e.target.dataset.visible = newVisible.toString()
	e.target.setAttribute('aria-expanded', newVisible.toString())
	e.target.getAttribute('aria-controls').split(' ').forEach((id) => {
		document.getElementById(id).dataset.visible = newVisible.toString()
	})
}
