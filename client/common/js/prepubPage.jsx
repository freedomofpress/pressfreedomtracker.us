import React from 'react'
import ParentSize from '../../charts/js/components/ParentSize'
import { createRoot } from 'react-dom/client'
import CategoryIcon from './components/categoryIcon'
import BarChart from '../../charts/js/components/BarChart'
import Tooltip from '../../charts/js/components/Tooltip'

function PrepubBarChart(props) {
	return (
		<ParentSize>
			{(parent) => <PrepubBarChartWidth {...props} parentWidth={parent.width} />}
		</ParentSize>
	)
}

function PrepubBarChartWidth({
	width,
	dataset,
	parentWidth
}) {
	const mobileBreakpoint = 670
	const chartWidth = parentWidth < mobileBreakpoint ? parentWidth : width
	const chartHeight = parentWidth < mobileBreakpoint ? 280 : 250
	const isMobileView = parentWidth < mobileBreakpoint
	return (
		<div className={'prepubChartContainer'} style={{ maxWidth: width}}>
			<div className={'prepubChart'}>
				<BarChart
					data={dataset}
					x={'date'}
					y={'count'}
					titleLabel={'incidents'}
					categoryColumn={'status'}
					allCategories={["confirmed", "unconfirmed"]}
					categoriesColors={{"unconfirmed": "#F4C280", "confirmed": "#E07A5F"}}
					id={'prepub-page-bar-chart'}
					width={chartWidth}
					height={chartHeight}
					isMobileView={isMobileView}
				/>
			</div>
		</div>
	)
}

function PrepubIncidentCategoryCount({
	incidentCount,
	categoryCounts,
}) {
	const [hovered, setHovered] = React.useState(false)
	const [focused, setFocused] = React.useState(false)
	const [tooltipPosition, setTooltipPosition] = React.useState({ x: 0, y: 0 })

	const updateTooltipPosition = (MouseEvent) => {
		const tooltipWidth = 250 // approximate width of the tooltip in px
		const tooltipHeight = 150 // approximate height of the tooltip in px
		const padding = 10 // padding from the mouse pointer

		let x = MouseEvent.clientX
		let y = MouseEvent.clientY

		// If tooltip would extend beyond the right edge of the window,
		// position it to the left of the cursor instead
		if (x + tooltipWidth + padding > window.innerWidth) {
			x = x - tooltipWidth
		}
		// If tooltip would extend beyond the bottom edge of the window,
		// center it vertically relative to the cursor
		if (y + tooltipHeight + padding > window.innerHeight) {
			y = y - tooltipHeight / 2
		}
		// If tooltip would extend beyond the top edge of the window,
		// position it below the cursor instead
		if (y < tooltipHeight) {
			y = y + tooltipHeight + padding
		}
		setTooltipPosition({ x: x, y: y })
	}
	return (
		<>
			{(hovered || focused) && (
				<Tooltip
					x={tooltipPosition.x}
					y={tooltipPosition.y}
					content={(
						<div className="category-count-tooltip">
							<p className="category-count-tooltip--heading">Categories tracked (unconfirmed)</p>
							{categoryCounts.map((item) => (
								<dl className="category-count-tooltip--row" key={item.category}>
									<dt className="category-count-tooltip--name">
										<CategoryIcon category={item.category} width={14} />
										{item.category}
									</dt>
									<dd className="category-count-tooltip--count">{item.count}</dd>
								</dl>
							))}
						</div>
					)}
				/>
			)}
			<span
				// eslint-disable-next-line jsx-a11y/no-noninteractive-tabindex
				tabIndex={0}
				className="unconfirmed-incidents--count"
				style={{ '--incident-count': incidentCount }}
				onMouseMove={updateTooltipPosition}
				onMouseEnter={(e) => {
					updateTooltipPosition(e)
					setHovered(true)
				}}
				onMouseLeave={() => {
					setHovered(false)
				}}
				onFocus={() => setFocused(true)}
				onBlur={() => setFocused(false)}
			>
				{incidentCount}
			</span>
		</>
	)
}

const chartContainers = Array.from(document.getElementsByClassName('js-prepub-bar-chart'))

chartContainers.forEach((node) => {
	const root = createRoot(node)
	const chartDataset = JSON.parse(node.dataset.chartDataset)
	root.render((
		<PrepubBarChart width={670} dataset={chartDataset} />
	))
})

const incidentCountContainers = Array.from(document.getElementsByClassName('js-unconfirmed-incidents-count'))

incidentCountContainers.forEach((node) => {
	const root = createRoot(node)
	const noJSFallbackElem = node.parentElement.querySelector('.no-js-fallback')
	// Hide the No JS fallback
	noJSFallbackElem.style.display ='none'
	const incidentCount = parseInt(node.dataset.incidentCount)
	const categoryCounts = JSON.parse(node.dataset.categoryCounts)
	root.render((
		<PrepubIncidentCategoryCount incidentCount={incidentCount} categoryCounts={categoryCounts} />
	))
})
