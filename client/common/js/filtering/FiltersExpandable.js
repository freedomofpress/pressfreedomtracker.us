import React from 'react'
import classNames from 'classnames'


function FiltersExpandable({ filtersExpanded, children }) {
	return (
		<div className={classNames(
			'filters__expandable',
			{ 'filters__expandable--expanded': filtersExpanded }
		)}>
			{children}
		</div>
	)
}


export default FiltersExpandable
