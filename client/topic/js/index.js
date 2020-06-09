import '@babel/polyfill'

import React from 'react'
import { render } from 'react-dom'

import CategoryGrid from './CategoryGrid'

const topicGridElements = document.getElementsByClassName('js-topic-grid-by-category')

Array.from(topicGridElements).forEach(el => {
	const props = {
		dataUrl: el.dataset.endpoint,
		dataUrlParams: JSON.parse(el.dataset.endpointParams),
	}
	render(<CategoryGrid {...props} />, el)
})
