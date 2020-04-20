import React from 'react'
import queryString from 'query-string'
import { HorizontalLoader } from '~/filtering/Loader'


function FiltersFooter({
	handleClearFilters,
	loading,
	pageFetchParams,
	filtersTouched,
	exportPath,
}) {
	const params = pageFetchParams
	const qs = queryString.stringify(params)
	const exportUrl = `${exportPath}?${qs}`
	return (
		<div className="filters__footer">
			<div className="filters__text filters__text--dim filters__text--meta">
				Need to do more complex filtering?
				{' '}
				<a href={exportUrl} className="filters__link">Download the Data.</a>
			</div>

			<span className="filters__button-toolbar">
				<button
					className="filters__button"
					onClick={handleClearFilters}
					type="button"
				>
					Clear Filters
				</button>

				<button
					className="filters__button filters__button--bordered filters__button--wide"
					disabled={!filtersTouched}
					type="submit"
				>
					{loading > 0 && <HorizontalLoader />}
					{loading === 0 && 'Apply Filters'}
				</button>
			</span>
		</div>
	)
}


export default FiltersFooter
