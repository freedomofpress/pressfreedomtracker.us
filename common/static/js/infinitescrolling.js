import axios from 'axios'
import { throttle, isElementVisible } from '~/utils'


class InfiniteScroller {
	constructor() {
		this.nextLinkElm = document.querySelector('.js-infinite-scrolling-next-link:last-child')
		this.parentElm = document.querySelector('.js-infinite-scrolling-parent')

		this.handleScroll = throttle(this.handleScroll.bind(this), 20)

		window.addEventListener('scroll', this.handleScroll)
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
				if (response.status === 200) {
					this.insertPageFromBody(response.data)
				}
			})
	}
}


document.addEventListener('DOMContentLoaded', () => new InfiniteScroller())
