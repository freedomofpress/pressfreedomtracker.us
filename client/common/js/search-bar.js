/* eslint-disable react/jsx-filename-extension, import/no-import-module-exports */
import React from 'react'
import { createRoot } from 'react-dom/client'
import Search from './components/Search'
import DataLoader from '../../charts/js/components/DataLoader'

const fields = [
	'categories',
	'authors',
	'date',
	'city',
	'state',
	'latitude',
	'longitude',
	'tags',
]

function engageSearchBars() {
	const params = new URLSearchParams([
		['fields', fields.join(',')],
		['format', 'csv'],
	])

	const searchBars = document.querySelectorAll('.search-bar')

	searchBars.forEach((searchBarNode) => {
		const selectedTags = searchBarNode.dataset.tags ? JSON.parse(searchBarNode.dataset.tags) : []

		const root = createRoot(searchBarNode)
		root.render((
			<DataLoader
				dataUrl={[`/api/edge/incidents/homepage_csv/?${params.toString()}`]}
				dataKey={['data']}
				loadingComponent={false}
			>
				<Search selectedTags={selectedTags} />
			</DataLoader>
		))
	})
}

engageSearchBars()

// Hot module reloading
if (module.hot) {
	module.hot.accept('components/Search', () => {
		console.clear()
		engageSearchBars()
	})
}
