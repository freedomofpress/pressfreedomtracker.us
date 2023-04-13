import React, { useEffect, useState } from 'react'
import PropTypes from 'prop-types'
import * as d3 from 'd3'
import 'regenerator-runtime/runtime'

function Loader() {
	return <div>Loading...</div>
}

function DataLoader({ dataUrl, dataParser, dataKey, loadingComponent, children }) {
	const [data, setData] = useState({})
	const [loading, setLoading] = useState(true)
	const [fetchCache, setFetchCache] = useState({})

	// Every time dataUrl or dataParser changes, fetch new data and parse it
	useEffect(() => {
		(() => {
			setLoading(true)

			// Convert singular strings into arrays
			const dataUrls = (typeof dataUrl === "string" ? [dataUrl] : dataUrl).filter(d => d)
			const dataKeys = (typeof dataKey === "string" ? [dataKey] : dataKey).filter(d => d)
			const dataParsers = (typeof dataParser === "function" ? [dataParser] : dataParser).filter(d => d)

			// Make sure that we have arrays
			if (!Array.isArray(dataUrls) || !Array.isArray(dataKeys) || !Array.isArray(dataParsers))
				return

			// Only fetch the data endpoints that we have url, key, and parser for
			const numDataFetchers = Math.min(dataKeys.length, dataUrls.length, dataParsers.length);

			const fetchData = []

			// Generate the promise for fetching data
			for (let i = 0; i < numDataFetchers; i++) {
				// Get the url, key, and parser for this entry
				const dataUrlEntry = dataUrls[i]
				const dataKeyEntry = dataKeys[i]
				const dataParserEntry = dataParser[i]

				// Get the cache key
				const fetchCacheKey = `${dataKeyEntry}-${dataUrlEntry}-${btoa(dataParserEntry.toString())}`

				// If this data has already been fetched, then simply get it from the cache
				if (fetchCache[fetchCacheKey]) fetchData.push(Promise.resolve(fetchCache[fetchCacheKey]))

				// Otherwise we load it and save it to the cache
				else fetchData.push(
					fetch(dataUrlEntry)
						.then(response => response.text())
						.then(text => dataParserEntry(text))
						.then(data => {
							setFetchCache({...fetchCache, [fetchCacheKey]: data})
							return Promise.resolve(data)
						})
				)
			}

			// Wait for all the data to be loaded (or attempted to be loaded)
			Promise.allSettled(fetchData).then(parsedData => {
				const data = {}

				// Save each successful response value into the data object
				parsedData.forEach(({ value }, i) => {
					if (value) data[dataKeys[i]] = value
				})

				// Set the data and unset loading
				setData(data)
				setLoading(false)
			})
		})()
	}, [dataUrl, dataParser, dataKey])

	// If data hasn't loaded yet, return the loading component instead
	if (loading && loadingComponent) return loadingComponent

	// Clone children with the added data prop and return it
	return React.cloneElement(children, data)
}

DataLoader.propTypes = {
	dataUrl: PropTypes.oneOfType([PropTypes.string, PropTypes.arrayOf(PropTypes.string)]).isRequired,
	dataParser: PropTypes.oneOfType([PropTypes.func, PropTypes.arrayOf(PropTypes.func)]),
	dataKey: PropTypes.oneOfType([PropTypes.string, PropTypes.arrayOf(PropTypes.string)]),
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
