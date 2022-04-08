import axios from 'axios'
import { throttle, isElementVisible } from './utils'

class ArticleLoader {
	constructor() {
		// ArticleLoader is a go! We can remove the Previous link
		// since we don't need it in the context of infinite scrolling.
		const prevLinkElm = document.querySelector('.js-article-loading-prev-link')
		if (prevLinkElm) {
			prevLinkElm.remove()
		}

		// We're going to keep track of the next link element so we can
		// replace it on load and use it for the next XHR URL.
		this.nextLinkElm = document.querySelector('.js-article-loading-next-link')

		// This is going to be our insertion parent for new items.
		this.parentElm = document.querySelector('.js-article-loading-parent')
		if ('paginationButtonText' in this.parentElm.dataset) {
			this.buttonText = this.parentElm.dataset.paginationButtonText
		} else {
			this.buttonText = 'Load More Posts'
		}
		this.nextLinkElm.innerText = this.buttonText

		// We're going to keep track of the number of fetches we've made
		// because only a certain number are going to occur automatically.
		this.fetches = 0
		this.shouldAutoFetch = true

		this.handleScroll = throttle(this.handleScroll.bind(this), 20)
		this.getNextPage = this.getNextPage.bind(this)

		window.addEventListener('scroll', this.handleScroll)
		const elm = document.querySelector('.js-article-loading-next-link')
		if (elm) {
			elm.addEventListener('click', this.getNextPage)
		}
	}

	incrementFetches() {
		this.fetches += 1
	}

	handleScroll() {
		if (this.fetches < ArticleLoader.NUM_AUTO_FETCHES) {
			const elm = this.parentElm.querySelector('.js-article-loading-item:last-child')
			if (isElementVisible(elm)) {
				this.getNextPage()
			}
		}
	}

	replaceIncidents(ajaxBodyHtml) {
		const tempElm = document.createElement('span')
		tempElm.innerHTML = ajaxBodyHtml

		const newItemList = tempElm.querySelector('.js-article-loading-parent')

		const fadeIn = (item, i) => {
			item.classList.add('animation-fade-in')
			item.classList.add(`animation-fade-in--${i + 1}`)
		}
		tempElm.querySelectorAll('.js-article-loading-item').forEach(fadeIn)

		const newNextLink = tempElm.querySelector('.js-article-loading-next-link')
		if (newNextLink) {
			newNextLink.addEventListener('click', this.getNextPage)
			if (!this.nextLinkElm) {
				this.parentElm.parentNode.appendChild(newNextLink)
			}
			this.nextLinkElm = newNextLink
		} else if (this.nextLinkElm) {
			this.nextLinkElm.remove()
			this.nextLinkElm = null
		}

		this.parentElm.parentNode.replaceChild(newItemList, this.parentElm)
		this.parentElm = newItemList
		const summaryTable = document.querySelector('.js-summary-table')
		const newSummaryTable = tempElm.querySelector('.js-summary-table')
		summaryTable.innerHTML = newSummaryTable.innerHTML

		const methodologies = document.querySelector('.js-methodologies')
		const newMethodologies = tempElm.querySelector('.js-methodologies')
		methodologies.innerHTML = newMethodologies.innerHTML
	}

	appendIncidents(ajaxBodyHtml) {
		const fragment = document.createDocumentFragment()
		const tempElm = document.createElement('span')
		tempElm.innerHTML = ajaxBodyHtml

		const items = tempElm.querySelectorAll('.js-article-loading-item')
		for (let i = 0; i < items.length; i += 1) {
			items[i].classList.add('animation-fade-in')
			items[i].classList.add(`animation-fade-in--${i + 1}`)
			fragment.appendChild(items[i])
		}

		// Swap the old next page link with the new
		const _elm = tempElm.querySelector('.js-article-loading-next-link')
		if (_elm) {
			_elm.addEventListener('click', this.getNextPage)
			_elm.innerText = this.buttonText
			if (this.nextLinkElm) {
				this.nextLinkElm.parentNode.replaceChild(_elm, this.nextLinkElm)
			}
			this.nextLinkElm = _elm
		} else if (this.nextLinkElm) {
			this.nextLinkElm.remove()
			this.nextLinkElm = null
		}

		this.parentElm.appendChild(fragment)
	}

	getNextPage(event) {
		if (event) {
			event.preventDefault()
		}

		if (this.isLoading) {
			return
		}

		const cameFromClick = event && event.target.className.indexOf('js-article-loading-next-link') !== -1
		if (!cameFromClick && !this.nextLinkElm) {
			return
		}

		this.isLoading = true
		this.nextLinkElm.innerHTML = '<div class="loader">Loading…</div>'

		axios.get(this.nextLinkElm.href)
			.then((response) => {
				this.isLoading = false
				this.incrementFetches()

				if (response.status === 200) {
					this.appendIncidents(response.data)
					const urlParams = new URLSearchParams(window.location.search)
					urlParams.set(
						'endpage',
						urlParams.has('endpage') ? parseInt(urlParams.get('endpage')) + 1 : 2,
					)
					window.history.replaceState(null, null, '?' + urlParams.toString())
				}
			})
	}
}

ArticleLoader.NUM_AUTO_FETCHES = 0

document.addEventListener('DOMContentLoaded', () => {
	if (window._articleLoader) {
		// eslint-disable-next-line no-console
		console.warn('An ArticleLoader instance already exists.')
		return
	}

	if (document.querySelector('.js-article-loading-parent')) {
		window._articleLoader = new ArticleLoader()
	}
})
