/* eslint-disable jsx-a11y/label-has-associated-control, no-case-declarations */
import React, { useState, createRef } from 'react'
import classNames from 'classnames'
import PropTypes from 'prop-types'
import CategoryIcon from './categoryIcon'
import { chooseTrendingTags } from '../../../charts/js/components/HomepageSelection'

const numberOfTags = 4

export default function Search({ data = [], selectedTags = [] }) {
	const [searchActive, setSearchActive] = useState(false)
	const [selectedTag, setSelectedTag] = useState()
	const [selectedCategory, setSelectedCategory] = useState()
	const [searchText, setSearchText] = useState('')
	const [searchTextCategories, setSearchTextCateogories] = useState([])

	// get a list of all categories
	const categories = Object.keys(data.reduce((categoryMap, incident) => {
		incident.categories
			.split(',')
			.map((category) => category.trim())
			.forEach((category) => {
				// eslint-disable-next-line no-param-reassign
				categoryMap[category] = true
			})
		return categoryMap
	}, {}))

	const frequentTags = (selectedTags && selectedTags.length)
		? selectedTags : chooseTrendingTags(data, numberOfTags)
	const inputRef = createRef()

	const updateSelectedTag = (tag) => () => {
		setSearchText('')
		setSelectedTag(tag)
		setSelectedCategory(null)
		inputRef?.current.focus()
	}

	const performCategorySearch = (category) => {
		window.location.href = `/all-incidents/?categories=${category}`
	}

	const performTagSearch = (tag) => {
		window.location.href = `/all-incidents/?tags=${tag}`
	}

	const updateSearchText = (text) => {
		if (selectedTag || selectedCategory) return
		setSelectedTag(null)
		setSelectedCategory(null)
		setSearchText(text)
		setSearchActive(true)

		// find the categories that are relevant to this search
		setSearchTextCateogories(
			categories.filter((category) => category.toLowerCase().indexOf(text.toLowerCase()) >= 0),
		)
	}

	const closeSearchActive = () => {
		inputRef?.current.focus()
		setSearchActive(false)
	}

	const handleArrowKeys = (event) => {
		const currentId = event.target.parentElement?.id || event.target.id
		const allDropdowns = [...document.querySelectorAll('.search-dropdown--tag, .search-dropdown--category')]
		let currentTagIndex

		switch (event.keyCode) {
		case 38: // up
			// select prev tag
			const dropdownsReversed = allDropdowns.reverse()
			currentTagIndex = dropdownsReversed.findIndex((tagEl) => tagEl.id === currentId)
			if (dropdownsReversed[currentTagIndex + 1]) dropdownsReversed[currentTagIndex + 1].querySelector('button').focus()
			event.preventDefault()
			break
		case 40: // down
			// select next tag
			currentTagIndex = allDropdowns.findIndex((tagEl) => tagEl.id === currentId) || 0
			if (allDropdowns[currentTagIndex + 1]) allDropdowns[currentTagIndex + 1].querySelector('button').focus()
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
		} else if (selectedCategory) {
			window.location.href = `/all-incidents/?categories=${selectedCategory}`
		}
	}

	let unselectable = (selectedTag != null || selectedCategory != null)
	// The base markup is the same as incidents/templates/incident/_search_bar.html
	return (
		<form
			className={classNames("search-form", {'smart-search--unselectable': unselectable})}
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
				placeholder={(!selectedTag && !selectedCategory) ? 'Search incidents' : ''}
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
				aria-expanded={
					searchActive && !selectedTag && !selectedCategory && !searchText && !!frequentTags.length
				}
			/>
			<button type="submit" className="btn btn-ghost search-button" value="Search">
				Search
			</button>

			{selectedCategory && (
				<div className="search-category-pill">
					<span className="search-category-pill--category-label">category: </span>
					<CategoryIcon category={selectedCategory} width={16} />
					{selectedCategory}
					<button
						type="button"
						className="search-category-pill--close"
						aria-label="Clear"
						onClick={updateSelectedTag(null)}
					>
						<i className="search-tag-pill--close--icon" aria-hidden />
						Clear
					</button>
				</div>
			)}

			{selectedTag && (
				<div className="search-tag-pill">
					<span className="search-tag-pill--tag-hash">#</span>
					{selectedTag}
					<button
						type="button"
						className="search-tag-pill--close"
						aria-label="Clear"
						onClick={updateSelectedTag(null)}
					>
						<i className="search-tag-pill--close--icon" aria-hidden />
						Clear
					</button>
				</div>
			)}

			{searchActive && !selectedTag && !selectedCategory && !!frequentTags.length && (
				<div className="search-dropdown" id="search-dropdown" role="listbox">
					{searchText ? (
						<>
							<div className="search-dropdown--header">
								Search term
							</div>
							<ul className="search-dropdown--wrap">
								<li
									id="smart-search-form-text"
									className="search-dropdown--tag"
									role="option"
									aria-selected={false}
								>
									<button
										className="search-dropdown--tag--button search-dropdown--tag--custom-search"
										type="button"
										onClick={closeSearchActive}
										onKeyDown={handleArrowKeys}
									>
										{`‘${searchText}’`}
									</button>
								</li>
							</ul>

							{searchTextCategories.length > 0 && (
								<>
									<hr />
									<div className="search-dropdown--header">
										Filter incidents by
									</div>
									<ul className="search-dropdown--wrap">
										{searchTextCategories.map((category, i) => (
											<li
												id={`smart-search-form-${i}`}
												key={category}
												className="search-dropdown--category"
												role="option"
												aria-selected={false}
											>
												<button
													className="search-dropdown--category--button"
													type="button"
													onClick={() => performCategorySearch(category)}
													onKeyDown={handleArrowKeys}
												>
													<span className="search-dropdown--tag--button--category-label">category:</span>
													<CategoryIcon category={category} />
													{category}
													<span className="search-dropdown__go">Go &#8594;</span>
												</button>
											</li>
										))}
									</ul>
								</>
							)}
						</>
					) : (
						<>
							<div className="search-dropdown--header">
								{(selectedTags && selectedTags.length) ? 'Trending Topics' : 'Frequently Used Tags'}
							</div>
							<ul className="search-dropdown--wrap">
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
											onClick={() => performTagSearch(tag)}
											onKeyDown={handleArrowKeys}
										>
											<span className="search-dropdown--tag--button--hash">#</span>
											{tag}
											<span className="search-dropdown__go">Go &#8594;</span>
										</button>
									</li>
								))}
							</ul>
						</>
					)}
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
