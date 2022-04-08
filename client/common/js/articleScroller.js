class ArticleScroller {
	constructor(scrollerElement) {
		// Since JS is loaded we can show the interactive horizontal scroller
		this.articleParent = document.getElementById(scrollerElement.dataset.articles)

		this.articleParent.classList.add('article-carousel__items--flex')
		scrollerElement.classList.add('article-carousel__scroller--visible')

		this.scrollNextBtn = scrollerElement.querySelector('.article-carousel__scroller--button-next')
		this.scrollPrevBtn = scrollerElement.querySelector('.article-carousel__scroller--button-prev')

		this.articles = this.articleParent.querySelectorAll('li')
		this.perArticleWidth = this.articles[0].getBoundingClientRect().width
		this.shift = 0

		this.scrollToLeft = this.scrollToLeft.bind(this)
		this.scrollToRight = this.scrollToRight.bind(this)

		if (!this.prevExists()) {
			this.scrollPrevBtn.disabled = true
		}

		if (!this.nextExists()) {
			this.scrollNextBtn.disabled = true
		}

		this.scrollNextBtn.addEventListener('click', this.scrollToLeft)
		this.scrollPrevBtn.addEventListener('click', this.scrollToRight)

		const self = this
		this.delay = 250
    	this.throttled = false

		window.addEventListener('resize', () => {
			if (!self.throttled) {
				self.scrollPrevBtn.disabled = !self.prevExists()
				self.scrollNextBtn.disabled = !self.nextExists()
				self.throttled = true
				setTimeout(function() {
				  	self.throttled = false
				}, self.delay)
			}
		});
	}

	static isVisible(article) {
		const rect = article.getBoundingClientRect()
		if (rect.x < 0 || rect.right > window.innerWidth) {
			return false
		}
		return true
	}

	shiftArticles(shift) {
		this.articleParent.style.transform = 'translateX(' + shift + ')'
	}

	prevExists() {
		return !ArticleScroller.isVisible(this.articles[0])
	}

	nextExists() {
		return !ArticleScroller.isVisible(this.articles[this.articles.length - 1])
	}

	scrollToLeft() {
		if (!this.nextExists()) {
			return
		}
		this.shift -= this.perArticleWidth + 8 // half of the gap to show prev & next
		this.shiftArticles(this.shift + 'px')

		// Check after 1s of scrolling whether button should be disabled or enabled
		setTimeout(() => {
			if (!this.nextExists()) {
				this.scrollNextBtn.disabled = true
			}
			this.scrollPrevBtn.disabled = false
		}, 1000)
	}

	scrollToRight() {
		if (!this.prevExists()) {
			return
		}
		this.shift += this.perArticleWidth + 8 // half of the gap to show prev & next
		this.shiftArticles(this.shift + 'px')

		// Check after 1s of scrolling whether button should be disabled or enabled
		setTimeout(() => {
			if (!this.prevExists()) {
				this.scrollPrevBtn.disabled = true
				return
			}
			this.scrollNextBtn.disabled = false
		}, 1000)
	}
}

document.addEventListener('DOMContentLoaded', () => {
	if (window._articleScrollers) {
		console.warn('ArticleScroller instances already exist.')
		return
	}

	window._articleScrollers = []

	document.querySelectorAll('[role=scroller]').forEach((scroller) => {
		window._articleScrollers.push(new ArticleScroller(scroller))
	})
})
