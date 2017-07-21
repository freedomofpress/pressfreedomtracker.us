import React from 'react'
import { HorizontalLoader } from '~/filtering/Loader'


function FiltersFooter({
	handleApplyFilters,
	handleClearFilters,
	loading,
	filtersTouched,
}) {
	return (
		<div className="filters__footer">
			<div className="filters__text filters__text--dim filters__text--meta">
				Need to do more complex filtering?
				{' '}
				<a href="#" className="filters__link">Download the Data.</a>
			</div>

			<span className="filters__button-toolbar">
				<button
					className="filters__button"
					onClick={handleClearFilters}
				>
					Clear Filters
				</button>

				<button
					className="filters__button filters__button--bordered filters__button--wide"
					onClick={handleApplyFilters}
					disabled={!filtersTouched}
				>
					{loading > 0 && <HorizontalLoader />}
					{loading === 0 && 'Apply Filters'}
				</button>
			</span>
		</div>
	)
}


export default FiltersFooter
