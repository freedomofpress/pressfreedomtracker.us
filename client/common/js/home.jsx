import React from "react"
import ReactDOM from "react-dom"
import { csv } from "d3"

import 'regenerator-runtime/runtime'

import HomepageMainCharts from '../../charts/js/components/HomepageMainCharts'

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

const main = async () => {
	const dataset = await csv(`/api/edge/incidents/?fields=${fields}&format=csv`)
	const chartContainers = Array.from(document.getElementsByClassName('js-homepage-charts'))

	chartContainers.forEach((node) => {
		ReactDOM.render(<div style={{ width: '100%' }}><HomepageMainCharts data={dataset} /></div>, node)
	})
}

main()
