import React, { useEffect, useState } from 'react'
import PropTypes from 'prop-types'
import * as d3 from 'd3'
import 'regenerator-runtime/runtime'

function Loader() {
	return <div>Loading...</div>
}

function DataLoader({ dataUrl, dataParser, dataKey, loadingComponent, children }) {
	const [data, setData] = useState([])
	const [loading, setLoading] = useState(true)

	// Every time dataUrl or dataParser changes, fetch new data and parse it
	useEffect(() => {
		(async () => {
			setLoading(true)
			const response = await fetch(dataUrl)
			const content = await response.text()
			const parsed = dataParser(content)
			setData(parsed)
			setLoading(false)
		})()
	}, [dataUrl, dataParser])

	// If data hasn't loaded yet, return the loading component instead
	if (loading) return loadingComponent

	// Clone children with the added data prop and return it
	const newChild = React.cloneElement(children, { [dataKey]: data })
	return newChild
}

DataLoader.propTypes = {
	dataUrl: PropTypes.string.isRequired,
	dataParser: PropTypes.func,
	dataKey: PropTypes.string,
	loadingComponent: PropTypes.node,
	children: PropTypes.node,
}

DataLoader.defaultProps = {
	dataParser: d3.csvParse,
	dataKey: 'data',
	loadingComponent: <Loader />,
	children: [],
}

export default DataLoader
