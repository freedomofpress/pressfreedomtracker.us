import React from "react"
import ReactDOM from "react-dom"

import HomepageMainCharts from '../../charts/js/components/HomepageMainCharts'
import DataLoader from "../../charts/js/components/DataLoader"

const fields = [
	'categories',
	'authors',
	'date',
	'city',
	'state',
	'latitude',
	'longitude',
	'tags',
].join(',')

const chartContainers = Array.from(document.getElementsByClassName('js-homepage-charts'))

chartContainers.forEach((node) => {
	ReactDOM.render((
		<DataLoader dataUrl={`/api/edge/incidents/?fields=${fields}&format=csv`}>
			<HomepageMainCharts />
		</DataLoader>
	), node)
})
