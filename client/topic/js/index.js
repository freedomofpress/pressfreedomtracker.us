import '@babel/polyfill'

import React from 'react'
import { render } from 'react-dom'

import CategoryGrid from './CategoryGrid'

const topicGridElements = document.getElementsByClassName('js-topic-grid-by-category')

Array.from(topicGridElements).forEach(el => {
	const props = {
		dataUrl: el.dataset.endpoint,
		incidentsPerModule: parseInt(el.dataset.incidentsPerModule)
	}
	render(<CategoryGrid {...props} />, el)
})
