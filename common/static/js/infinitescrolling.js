import axios from 'axios'
import { throttle, isElementVisible } from '~/utils'


class InfiniteScroller {
	constructor() {
		// InfiniteScroller is a go! We can remove the Previous link
		// since we don't need it in the context of infinite scrolling.
		const prevLinkElm = document.querySelector('.js-infinite-scrolling-prev-link')
		if (prevLinkElm) {
			prevLinkElm.remove()
		}

		// We're going to keep track of the next link element so we can
		// replace it on load and use it for the next XHR URL.
		this.nextLinkElm = document.querySelector('.js-infinite-scrolling-next-link:last-child')

		// This is going to be our insertion parent for new items.
		this.parentElm = document.querySelector('.js-infinite-scrolling-parent')

		// We're going to keep track of the number of fetches we've made
		// because only a certain number are going to occur automatically.
		this.fetches = 0
		this.shouldAutoFetch = true

		this.handleScroll = throttle(this.handleScroll.bind(this), 20)
		this.getNextPage = this.getNextPage.bind(this)

		window.addEventListener('scroll', this.handleScroll)
	}

	incrementFetches() {
		if (++this.fetches == InfiniteScroller.NUM_AUTO_FETCHES) {
			this.shouldAutoFetch = false
		}
	}

	handleScroll(event) {
		if (this.shouldAutoFetch) {
			const elm = this.parentElm.querySelector('.js-infinite-scrolling-item:last-child')
			if (isElementVisible(elm)) {
				this.getNextPage()
			}
		}
	}

	insertPageFromBody(ajaxBodyHtml) {
		const fragment = document.createDocumentFragment()
		const tempElm = document.createElement('span')
		tempElm.innerHTML = ajaxBodyHtml

		const parentElm = tempElm.querySelector('.js-infinite-scrolling-parent')

		const items = tempElm.querySelectorAll('.js-infinite-scrolling-item')
		for (var i = 0; i < items.length; i++) {
			items[i].classList.add('animation-fade-in')
			items[i].classList.add(`animation-fade-in--${i + 1}`)
			fragment.appendChild(items[i])
		}

		// Swap the old next page link with the new
		const _elm = tempElm.querySelector('.js-infinite-scrolling-next-link:last-child')
		if (_elm) {
			_elm.addEventListener('click', this.getNextPage)
			this.nextLinkElm.parentNode.replaceChild(_elm, this.nextLinkElm)
			this.nextLinkElm = _elm
		} else {
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

		const cameFromClick = event && event.target.className.indexOf('js-infinite-scrolling-next-link') !== -1
		if (!cameFromClick && !this.nextLinkElm) {
			return null
		}

		this.isLoading = true
		this.nextLinkElm.innerHTML = '<div class="loader">Loading…</div>'

		axios.get(this.nextLinkElm.href)
			.then(response => {
				this.isLoading = false
				this.incrementFetches()

				if (response.status === 200) {
					this.insertPageFromBody(response.data)
				}
			})
	}
}


InfiniteScroller.NUM_AUTO_FETCHES = 1


document.addEventListener('DOMContentLoaded', () => {
	if (document.querySelector('.js-infinite-scrolling-parent')) {
		new InfiniteScroller()
	}
})
