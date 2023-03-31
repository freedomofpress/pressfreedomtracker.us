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
		this.updateNextPrevButtons = this.updateNextPrevButtons.bind(this)

		if (!this.prevExists()) {
			this.scrollPrevBtn.disabled = true
		}

		if (!this.nextExists()) {
			this.scrollNextBtn.disabled = true
		}

		this.scrollNextBtn.addEventListener('click', this.scrollToLeft)
		this.scrollPrevBtn.addEventListener('click', this.scrollToRight)
		this.articleParent.addEventListener('scroll', this.updateNextPrevButtons)
		window.addEventListener('resize', this.updateNextPrevButtons)
	}

	shiftArticles(shift) {
		this.articleParent.scrollLeft = shift
	}

	prevExists() {
		return this.articleParent.scrollLeft > 0
	}

	nextExists() {
		return (this.articleParent.scrollWidth - this.articleParent.scrollLeft)
			> this.articleParent.clientWidth
	}

	updateNextPrevButtons() {
		this.scrollNextBtn.disabled = false
		this.scrollPrevBtn.disabled = false
		if (!this.nextExists()) {
			this.scrollNextBtn.disabled = true
		}
		if (!this.prevExists()) {
			this.scrollPrevBtn.disabled = true
		}
	}

	scrollToLeft() {
		if (!this.nextExists()) {
			return
		}
		this.shift += this.perArticleWidth + 8 // half of the gap to show prev & next
		this.shiftArticles(this.shift)
	}

	scrollToRight() {
		if (!this.prevExists()) {
			return
		}
		this.shift -= this.perArticleWidth + 8 // half of the gap to show prev & next
		this.shiftArticles(this.shift)
	}
}

document.addEventListener('DOMContentLoaded', () => {
	if (window._articleScrollers) {
		// eslint-disable-next-line no-console
		console.warn('ArticleScroller instances already exist.')
		return
	}

	window._articleScrollers = []

	document.querySelectorAll('[role=scroller]').forEach((scroller) => {
		window._articleScrollers.push(new ArticleScroller(scroller))
	})
})
