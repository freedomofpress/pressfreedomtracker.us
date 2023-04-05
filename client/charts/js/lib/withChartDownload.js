import React, { useState } from 'react'
import { Canvg } from 'canvg'

const withChartDownload = (WrappedComponent) => (props) => {
	const [svgEl, setSvgEl] = useState()

	const downloadImage = () => {
		if (svgEl) {
			const canvas = document.createElement('canvas')
			const ctx = canvas.getContext('2d')

			Canvg.from(ctx, svgEl).then(() => {
				const link = document.createElement("a");
				link.href = canvas.toDataURL();
				link.download = 'chart.png';
				link.click();
			})
		}
	}

	return (<WrappedComponent {...props} setSvgEl={setSvgEl} />)
}

export default withChartDownload
