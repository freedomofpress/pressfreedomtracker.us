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

		this.handleScroll = throttle(this.handleScroll.bind(this), 20)

		window.addEventListener('scroll', this.handleScroll)
	}

	incrementFetches() {
		if (++this.fetches == InfiniteScroller.NUM_AUTO_FETCHES) {
			window.removeEventListener('scroll', this.handleScroll)
		}
	}

	handleScroll(event) {
		const elm = this.parentElm.querySelector('.js-infinite-scrolling-item:last-child')
		if (isElementVisible(elm)) {
			this.getNextPage()
		}
	}

	insertPageFromBody(ajaxBodyHtml) {
		const fragment = document.createDocumentFragment()
		const tempElm = document.createElement('span')
		tempElm.innerHTML = ajaxBodyHtml
		const items = tempElm.querySelectorAll('.js-infinite-scrolling-item')
		for (var i = 0; i < items.length; i++) {
			fragment.appendChild(items[i])
		}

		// Swap the old next page link with the new
		const _elm = tempElm.querySelector('.js-infinite-scrolling-next-link:last-child')
		if (_elm) {
			this.nextLinkElm.parentNode.replaceChild(_elm, this.nextLinkElm)
			this.nextLinkElm = _elm
		} else {
			this.nextLinkElm.remove()
			this.nextLinkElm = null
		}

		this.parentElm.appendChild(fragment)
	}

	getNextPage() {
		if (this.isLoading) {
			return
		}

		if (!this.nextLinkElm) {
			return null
		}

		this.isLoading = true
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


document.addEventListener('DOMContentLoaded', () => new InfiniteScroller())
