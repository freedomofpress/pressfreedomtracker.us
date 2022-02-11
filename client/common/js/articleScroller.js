class ArticleScroller {
	constructor() {
		// Since JS is loaded we can show the interactive horizontal scroller
		document.querySelector('.blog-list__posts--featured').classList.add('blog-list__posts--featured-flex')
		document.querySelector('.blog-list__featured-scroller').classList.add('blog-list__featured-scroller--visible')

		this.scrollNextBtn = document.querySelector('.blog-list__featured-scroller--button-next')
		this.scrollPrevBtn = document.querySelector('.blog-list__featured-scroller--button-prev')

		this.articleParent = document.querySelector('.blog-list__posts--featured-flex')
		this.articles = this.articleParent.querySelectorAll('.blog-list__item--featured')
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
	if (window._articleScroller) {
		console.warn('An ArticleScroller instance already exists.')
		return
	}

	if (document.querySelector('.blog-list__featured-scroller')) {
		window._articleScroller = new ArticleScroller()
	}
})
