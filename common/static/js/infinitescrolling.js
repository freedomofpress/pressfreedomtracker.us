import axios from 'axios'
import invariant from 'invariant'


function insertPageFromBody(ajaxBodyHtml) {
	const fragment = document.createDocumentFragment()
	const tempElm = document.createElement('span')
	tempElm.innerHTML = ajaxBodyHtml
	const items = tempElm.querySelectorAll('.js-infinite-scrolling-item')
	for (var i = 0; i < items.length; i++) {
		fragment.appendChild(items[i])
	}

	document.querySelector('.js-infinite-scrolling-parent').appendChild(fragment)
}


function nextPage() {
	axios.get('http://localhost:8000/all-incidents/?page=2')
		.then(function(response) {
			if (response.status === 200) {
				insertPageFromBody(response.data)
			}
		})
}


document.addEventListener('DOMContentLoaded', nextPage)
