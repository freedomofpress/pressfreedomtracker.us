import React from 'react'
import { createRoot } from 'react-dom/client'
import BarChart from "../../charts/js/components/BarChart"


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


const chartContainers = Array.from(document.getElementsByClassName('js-prepub-bar-chart'))

chartContainers.forEach((node) => {
	const root = createRoot(node)
	const chartDataset = JSON.parse(node.dataset.chartDataset)
	root.render((
		<PrepubBarChart width={1080} dataset={chartDataset} />
	))
})
