/* ContentWarningImage
 *
 * This is a web component wrapper around an image that adds a content
 * warning screen with a button and allows for dismissing warning and
 * showing image.
 *
 * It adds the cw-image-container class to address the styling and to toggle
 * the content warning blurring. It also adds a button to remove the
 * content warning blurring
 *
 * Example usage:
 *
 *     <cw-image>
 *         <label for="field-id">Field Name</label>
 *         <input type="text" id="field-id" />
 *     </cw-image>
 */
class ContentWarningImage extends HTMLElement {
	constructor() {
		super()

		// State
		this.blurred = true
	}

	connectedCallback() {
		// Elements
		this.classList.add('cw-image-container')
		this.imgElem = this.querySelector('img')
		this.dismissBtn = document.createElement('button')
		this.dismissBtn.classList.add('btn', 'btn-bordered')
		this.dismissBtn.textContent = this.dataset.warningText
		this.appendChild(this.dismissBtn)

		// Events
		this.dismissBtn.addEventListener('click', (e) => this.handleDismiss(e))

		// Run first DOM update
		this.updateDom()
	}

	handleDismiss() {
		this.blurred = false
		this.updateDom()
	}

	updateDom() {
		this.classList.toggle('blurred', this.blurred)
	}
}

customElements.define('cw-image', ContentWarningImage)
