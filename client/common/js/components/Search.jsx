/* eslint-disable jsx-a11y/label-has-associated-control */
import React, { useState } from 'react'
import classNames from 'classnames'
// eslint-disable-next-line import/named
import PropTypes from 'prop-types'
import { chooseMostFrequentTags } from '../../../charts/js/components/HomepageSelection'

const numberOfTags = 5

export default function Search({ data = [] }) {
	const [searchActive, setSearchActive] = useState(false)

	const selectedTags = chooseMostFrequentTags(data, numberOfTags)
	console.log(selectedTags)

	// The base markup is the same as incidents/templates/incident/_search_bar.html
	return (
		<form className="search-form">
			<label htmlFor="primary-search-bar" className="sr-only">
				Search incidents by text
			</label>
			<input
				id="primary-search-bar"
				placeholder="Search incidents by text"
				spellCheck="false"
				autoComplete="off"
				type="search"
				className={classNames('text-field--search-bar', searchActive && 'smart-search-active')}
				name="search"
				onFocus={() => setSearchActive(true)}
				onBlur={() => setSearchActive(false)}
			/>
			<button type="submit" className="btn btn-ghost search-button" value="Search">
				Search
			</button>

			{searchActive && (
				<div className="search-dropdown">
					<div className="search-dropdown--header">Trending Topics</div>
					<div className="search-dropdown--category">
						Test Category
					</div>
				</div>
			)}
		</form>
	)
}

Search.propTypes = {
	// eslint-disable-next-line react/forbid-prop-types
	data: PropTypes.array,
}

Search.defaultProps = {
	data: [],
}
