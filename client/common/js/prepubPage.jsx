import React from 'react'
import { createRoot } from 'react-dom/client'
import CategoryIcon from './components/categoryIcon'
import BarChart from '../../charts/js/components/BarChart'
import Tooltip from '../../charts/js/components/Tooltip'

function PrepubBarChart({
	width,
	dataset,
}) {
	return (
		<div className={'prepubChartContainer'} style={{ width: width}}>
			<div className={'prepubChart'}>
				<BarChart
					data={dataset}
					x={'date'}
					y={'count'}
					titleLabel={'incidents'}
					categoryColumn={'status'}
					allCategories={["confirmed", "unconfirmed"]}
					categoriesColors={{"unconfirmed": "#EEEEEE"}}
					id={'prepub-page-bar-chart'}
					width={width}
					height={540}
					isMobileView={false}
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
		setTooltipPosition({ x: MouseEvent.clientX, y: MouseEvent.clientY })
	}
	console.log(categoryCounts)
	return (
		<>
			{(hovered || focused) && (
				<Tooltip
					x={tooltipPosition.x}
					y={tooltipPosition.y}
					content={(
						<div className="category-count-tooltip">
							<p className="category-count-tooltip--heading">Categories Tracked (unconfirmed)</p>
							{categoryCounts.map((item) => (
								<dl className="category-count-tooltip--row">
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
		<PrepubBarChart width={1080} dataset={chartDataset} />
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
