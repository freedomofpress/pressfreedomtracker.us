class TabInterface {

	constructor(el, opts = {
		tabQuerySelector: 'a',
		getIdFromTab: t => t.href.split('#')[1]
	}) {
		const { tabQuerySelector, getIdFromTab } = opts

		// Collect the tabs together
		this._el = el
		this._opts = opts
		this._tabElements = Array.from(this._el.querySelectorAll(tabQuerySelector))
		this.tabs = this._tabElements.map(t => ({
			id: getIdFromTab(t),
			tab: t,
			panel: document.getElementById(getIdFromTab(t)),
		}))


		// Bind event handlers
		this.handleTabClick = this.handleTabClick.bind(this)

		// Bind events
		this.tabs.forEach(t => t.tab.addEventListener('click', this.handleTabClick))

		// Add ARIA properties
		this._el.setAttribute('role', 'tablist')
		this.tabs.forEach(t => {
			// Tab attributes
			t.tab.setAttribute('role', 'tab')
			t.tab.setAttribute('id', `${t.id}-label`)

			// Tab panel attributes
			t.panel.setAttribute('role', 'tabpanel')
			t.panel.setAttribute('aria-labelledby', `${t.id}-label`)
		})

		// Activate first tab
		this.activateTab(this.tabs[0].id)
	}

	handleTabClick(e) {
		this.activateTab(this._opts.getIdFromTab(e.currentTarget))
		e.preventDefault()
	}

	activateTab(id) {
		const newActiveTab = this.tabs.find(t => t.id === id)
		const newInactiveTab = this.tabs.filter(t => t.id !== id)

		newActiveTab.panel.removeAttribute('hidden')
		newActiveTab.tab.classList.add('active')
		newActiveTab.tab.setAttribute('aria-selected', 'true')

		newInactiveTab.forEach(t => {
			t.panel.setAttribute('hidden', 'hidden')
			t.tab.classList.remove('active')
			t.tab.removeAttribute('aria-selected')
		})
	}
}

document.addEventListener('DOMContentLoaded', e => {
	Array.from(document.querySelectorAll('.js-tabs')).forEach(t => new TabInterface(t))
})
