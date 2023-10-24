/* eslint-disable jsx-a11y/label-has-associated-control, no-case-declarations */
import React, { useState } from 'react'
import classNames from 'classnames'
import PropTypes from 'prop-types'
import { chooseMostFrequentTags } from '../../../charts/js/components/HomepageSelection'

const numberOfTags = 4

export default function Search({ data = [] }) {
	const [searchActive, setSearchActive] = useState(false)
	const [selectedTag, setSelectedTag] = useState()
	const [searchText, setSearchText] = useState('')

	const frequentTags = chooseMostFrequentTags(data, numberOfTags)

	const updateSelectedTag = (tag) => {
		setSearchText('')
		setSelectedTag(tag)
	}

	const updateSearchText = (text) => {
		if (selectedTag) return
		setSelectedTag(null)
		setSearchText(text)
	}

	const handleArrowKeys = (event) => {
		const currentId = event.target.id
		switch (event.keyCode) {
		case 38: // up
			// select prev tag
			const allTags = [...document.querySelectorAll('.search-dropdown--tag')].reverse()
			const currentTagIndex = allTags.findIndex((tagEl) => tagEl.id === currentId)
			if (allTags[currentTagIndex + 1]) allTags[currentTagIndex + 1].focus()
			event.preventDefault()
			break
		case 40: // down
			// select next tag
			const nextEl = document.querySelector(
				`#${currentId} ~ .search-dropdown--tag, #${currentId} ~ .search-dropdown .search-dropdown--tag`,
			)
			if (nextEl) nextEl.focus()
			event.preventDefault()
			break
		default:
		}
	}

	const handleSubmit = (event) => {
		event.preventDefault()
		if (searchText) {
			window.location.href = `/all-incidents/?search=${searchText}`
		} else if (selectedTag) {
			window.location.href = `/all-incidents/?tags=${selectedTag}`
		}
	}

	// The base markup is the same as incidents/templates/incident/_search_bar.html
	return (
		<form
			className="search-form"
			onSubmit={handleSubmit}
			onFocus={() => setSearchActive(true)}
			onBlur={(e) => {
				if (!e.currentTarget.contains(e.relatedTarget)) {
					setSearchActive(false)
				}
			}}
		>
			<label htmlFor="primary-search-bar" className="sr-only">
				Search incidents by text
			</label>
			<input
				id="primary-search-bar"
				placeholder={!selectedTag ? 'Search incidents' : ''}
				spellCheck="false"
				autoComplete="off"
				type="search"
				className={classNames('text-field--search-bar', searchActive && 'smart-search-active')}
				name="search"
				value={searchText}
				onKeyDown={handleArrowKeys}
				onChange={(e) => updateSearchText(e.target.value)}
			/>
			<button type="submit" className="btn btn-ghost search-button" value="Search">
				Search
			</button>

			{searchActive && !selectedTag && !searchText && !!frequentTags.length && (
				<div className="search-dropdown">
					<div className="search-dropdown--header">Trending Topics</div>
					{frequentTags.map((tag, i) => (
						<button
							type="button"
							id={`smart-search-form-${i}`}
							key={tag}
							className="search-dropdown--tag"
							onClick={() => updateSelectedTag(tag)}
							onKeyDown={handleArrowKeys}
							tabIndex="0"
						>
							<span className="search-dropdown--tag--hash">#</span>
							{tag}
						</button>
					))}
				</div>
			)}

			{selectedTag && (
				<div className="search-tag-pill">
					<span className="search-tag-pill--tag-hash">#</span>
					{selectedTag}
					<button
						type="button"
						className="search-tag-pill--close"
						onClick={() => updateSelectedTag(null)}
					>
						<i className="search-tag-pill--close--icon" />
					</button>
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
