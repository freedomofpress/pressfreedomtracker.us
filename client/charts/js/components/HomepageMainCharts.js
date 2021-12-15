import React, { useState } from "react";
import { TreeMap } from "./TreeMap.js";
import { USMap } from "./USMap.js";
import { BarChartHomepage } from "./BarChartHomepage.js";

export function HomepageMainCharts({
	data: dataset,
	isLastSixMonths,
	selectedYear,
	width,
}) {
	const [dimensions, setDimensions] = React.useState({
		width: window.innerWidth - 30,
	});
	React.useEffect(() => {
		function handleResize() {
			setDimensions({
				width: window.innerWidth - 30,
			});
		}

		window.addEventListener("resize", handleResize);

		return (_) => {
			window.removeEventListener("resize", handleResize);
		};
	});

	const chartWidth =
		dimensions.width > 970 ? dimensions.width / 3 : dimensions.width;
	const chartHeight = dimensions.width > 970 ? 500 : 480;

	return (
		<>
			<div className={"hpChartContainer"} style={{ width: dimensions.width }}>
				<div className={"hpChart"}>
					<TreeMap
						data={dataset}
						width={chartWidth}
						height={chartHeight}
						isHomePageDesktopView={dimensions.width > 970 ? true : false}
						minimumBarHeight={10}
					/>
				</div>
				<div className={"hpChart"}>
					<USMap data={dataset} width={chartWidth} height={chartHeight} />
				</div>
				<div className={"hpChart"}>
					<BarChartHomepage
						data={dataset}
						isLastSixMonths={isLastSixMonths}
						selectedYear={selectedYear}
						width={chartWidth}
						height={chartHeight}
					/>
				</div>
			</div>
		</>
	);
}
