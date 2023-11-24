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

export default function FilterSummary({ serializedFilters }) {
	const categoryFilters = JSON.parse(serializedFilters)

	const idMap = categoryFilters.reduce((acc, val) => ({ ...acc, [val.id]: val.title }), {});
	const allFilters = categoryFilters.flatMap(category => category.filters).reduce(
		(acc, val) => ({...acc, [val.name]: val})
	)

	const displayText = (filterName, value) => {
		const filter = allFilters[filterName]
		if (filter?.type == "bool") {
			return (value === '1') ? filter.present_summary_name : filter.absent_summary_name
		} else {
			return value.replaceAll("_", " ").toLowerCase()
		}
	}

	const searchParams = new URLSearchParams(window.location.search)
	const {
		categories: categoriesStr,
		tags: tagsStr,
		date_lower,
		date_upper,
		...restFilters
	} = Object.fromEntries(searchParams)

	const categories = [...new Set(
		(categoriesStr ? categoriesStr.split(',').map(d => d.trim()) : [])
			.map(category => {
				if (symbolMap[category]) return category;
				if (idMap[category]) return idMap[category];
				return null;
			})
			.filter(d => d)
	)]

	const tags = tagsStr ? tagsStr.split(',').map(d => d.trim()) : []

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
						aria-label={`Removes filter: ${category.toLowerCase()}`}
					>
						{symbolMap[category] && <div className={classNames("category", `category-${symbolMap[category]}`)}></div>}
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
						aria-label={`Removes start date: ${date_lower}`}
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
						aria-label={`Removes end date: ${date_upper}`}
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
							"tags", tags.filter(d => d !== tag).join(',')
						)}
						className="btn btn-tag"
						aria-label={`Removes tag: ${tag.toLowerCase()}`}
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
						aria-label={`Removes filter: ${restFilters[filterKey].replaceAll("_", " ").toLowerCase()}`}
					>
						<span>{displayText(filterKey, restFilters[filterKey])}</span>
						<span className="close-icon" />
					</button>
				</li>
			))}
		</ul>
	)
}
