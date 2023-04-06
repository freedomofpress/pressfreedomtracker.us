import React, { useState, useEffect } from 'react'
import { Canvg } from 'canvg'

const ChartDownloader = ({ children }) => {
	const [svgEl, setSvgEl] = useState()

	const downloadImage = () => {
		if (svgEl) {
			const canvas = document.createElement('canvas')
			const ctx = canvas.getContext('2d')
			const svgStringData = new XMLSerializer().serializeToString(svgEl);

			const canvg = Canvg.fromString(ctx, svgStringData, {})

			canvg.render().then(() => {
				const link = document.createElement("a");
				link.href = canvas.toDataURL();
				link.download = 'chart.png';
				link.click();
			})
		}
	}

	// Clone children with the added data prop and return it
	const chartEl = React.cloneElement(children, { setSvgEl })

	return (
		<>
			<button onClick={downloadImage}>Download Me</button>
			{chartEl}
		</>
	)
}

export default ChartDownloader
