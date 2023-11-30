/* eslint-disable jsx-a11y/label-has-associated-control, no-case-declarations */
import React, { useState, createRef } from 'react'
import classNames from 'classnames'
import PropTypes from 'prop-types'
import { chooseTrendingTags } from '../../../charts/js/components/HomepageSelection'

const numberOfTags = 4

export default function Search({ data = [], selectedTags = [] }) {
	const [searchActive, setSearchActive] = useState(false)
	const [selectedTag, setSelectedTag] = useState()
	const [searchText, setSearchText] = useState('')

	const frequentTags = (selectedTags && selectedTags.length)
		? selectedTags : chooseTrendingTags(data, numberOfTags)
	const inputRef = createRef()

	const updateSelectedTag = (tag) => () => {
		setSearchText('')
		setSelectedTag(tag)
		inputRef?.current.focus()
	}

	const updateSearchText = (text) => {
		if (selectedTag) return
		setSelectedTag(null)
		setSearchText(text)
	}

	const handleArrowKeys = (event) => {
		const currentId = event.target.parentElement?.id || event.target.id
		switch (event.keyCode) {
		case 38: // up
			// select prev tag
			const allTags = [...document.querySelectorAll('.search-dropdown--tag')].reverse()
			const currentTagIndex = allTags.findIndex((tagEl) => tagEl.id === currentId)
			if (allTags[currentTagIndex + 1]) allTags[currentTagIndex + 1].querySelector('button').focus()
			event.preventDefault()
			break
		case 40: // down
			// select next tag
			const nextEl = document.querySelector(
				`#${currentId} ~ .search-dropdown--tag, #${currentId} ~ .search-dropdown .search-dropdown--tag`,
			)
			if (nextEl) nextEl.querySelector('button').focus()
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
				ref={inputRef}
				placeholder={!selectedTag ? 'Search incidents' : ''}
				spellCheck="false"
				autoComplete="off"
				type="search"
				className={classNames('text-field--search-bar', searchActive && 'smart-search-active')}
				name="search"
				value={searchText}
				onKeyDown={handleArrowKeys}
				onChange={(e) => updateSearchText(e.target.value)}
				role="combobox"
				aria-haspopup="listbox"
				aria-controls="search-dropdown"
				aria-expanded={searchActive && !selectedTag && !searchText && !!frequentTags.length}
			/>
			<button type="submit" className="btn btn-ghost search-button" value="Search">
				Search
			</button>

			{selectedTag && (
				<div className="search-tag-pill">
					<span className="search-tag-pill--tag-hash">#</span>
					{selectedTag}
					<button
						type="button"
						className="search-tag-pill--close"
						aria-label="Close"
						onClick={updateSelectedTag(null)}
					>
						<i className="search-tag-pill--close--icon" aria-hidden />
					</button>
				</div>
			)}

			{searchActive && !selectedTag && !searchText && !!frequentTags.length && (
				<div className="search-dropdown" id="search-dropdown" role="listbox">
					<ul className="search-dropdown--header">{(selectedTags && selectedTags.length) ? 'Trending Topics' : 'Frequently Used Tags'}</ul>
					{frequentTags.map((tag, i) => (
						<li
							id={`smart-search-form-${i}`}
							key={tag}
							className="search-dropdown--tag"
							role="option"
							aria-selected={false}
						>
							<button
								className="search-dropdown--tag--button"
								type="button"
								onClick={updateSelectedTag(tag)}
								onKeyDown={handleArrowKeys}
							>
								<span className="search-dropdown--tag--button--hash">#</span>
								{tag}
							</button>
						</li>
					))}
				</div>
			)}
		</form>
	)
}

Search.propTypes = {
	// eslint-disable-next-line react/forbid-prop-types
	data: PropTypes.array,
	// eslint-disable-next-line react/forbid-prop-types
	selectedTags: PropTypes.array,
}

Search.defaultProps = {
	data: [],
	selectedTags: [],
}
