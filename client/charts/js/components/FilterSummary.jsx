import React from 'react'
import classNames from 'classnames'

const symbolMap = {
	"Arrest / Criminal Charge": "arrest",
	"Border Stop": "border_stop",
	"Denial of Access": "denial_of_access",
	"Equipment Search or Seizure": "equipment_search",
	"Assault": "assault",
	"Leak Case": "leak_case",
	"Subpoena / Legal Order": "subpoena",
	"Equipment Damage": "equipment_damage",
	"Prior Restraint": "prior_restraint",
	"Chilling Statement": "chilling_statement",
	"Other Incident": "other_incident",
}

export default function FilterSidebar() {
	const searchParams = new URLSearchParams(window.location.search)
	const {
		categories: categoriesStr,
		tags: tagsStr,
		date_lower,
		date_upper,
		...restFilters
	} = Object.fromEntries(searchParams)

	const categories = categoriesStr.split(',').map(d => d.trim())
	const tags = tagsStr.split(',').map(d => d.trim())

	const clearFilter = (filterKey, newFilterValue) => {
		const url = new URL(window.location);
		const newSearchParams = new URLSearchParams(window.location.search)

		if (newFilterValue) newSearchParams.set(filterKey, newFilterValue)
		else newSearchParams.delete(filterKey)

		url.search = newSearchParams.toString()
		window.location = url.toString()
	}

	return (
		<ul className="filters-summary">
			{categories.map(category => (
				<li key={category}>
					<button
						onClick={() => clearFilter(
							"categories", categories.filter(d => d !== category).join(',')
						)}
						className="btn btn-tag"
						tabIndex={0}
					>
						<div className={classNames("category", `category-${symbolMap[category]}`)}></div>
						<span>{category.toLowerCase()}</span>
						<span className="close-icon" />
					</button>
				</li>
			))}
			{date_lower && (
				<li>
					<button
						onClick={() => clearFilter("date_lower")}
						className="btn btn-tag"
						tabIndex={0}
					>
						<span>from: {date_lower}</span>
						<span className="close-icon" />
					</button>
				</li>
			)}
			{date_upper && (
				<li>
					<button
						onClick={() => clearFilter("date_upper")}
						className="btn btn-tag"
						tabIndex={0}
					>
						<span>to: {date_upper}</span>
						<span className="close-icon" />
					</button>
				</li>
			)}
			{tags.map(tag => (
				<li key={tag}>
					<button
						onClick={() => clearFilter(
							"tags", categories.filter(d => d !== tag).join(',')
						)}
						className="btn btn-tag"
						tabIndex={0}
					>
						<span>{tag.toLowerCase()}</span>
						<span className="close-icon" />
					</button>
				</li>
			))}
			{Object.keys(restFilters).map(filterKey => (
				<li key={restFilters[filterKey]}>
					<button
						onClick={() => clearFilter(filterKey)}
						className="btn btn-tag"
						tabIndex={0}
					>
						<span>{restFilters[filterKey].replaceAll("_", " ").toLowerCase()}</span>
						<span className="close-icon" />
					</button>
				</li>
			))}
		</ul>
	)
}
