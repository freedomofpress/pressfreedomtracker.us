import React, { useState } from 'react'
import classNames from 'classnames'
import { Canvg } from 'canvg'

/**
 * ChartDownloader Wrapper Component
 *
 * This wrapper component wraps a child component which allows a child component to "bind"
 * to an existing SVG node and provide functions for downloading that component as an
 * image.
 *
 * To use, the wrapped child component will receive a prop setSvgEl which is a function
 * that will be called to bind the svg element. Essentially it will look something like:
 *
 * ```
 * <ChartDownloader>
 *   <ChartComponent />
 * </ChartDownloader>
 * ```
 *
 * and the ChartComponent will have to do something like:
 *
 * ```
 * export default function ChartComponent({ setSvgEl }) {
 *   return (
 *     <svg ref={setSvgEl} />
 *   )
 * }
 * ```
 *
 * @param children
 * @param downloadFileName
 * @param imageWidth
 * @param showDownloadButton
 * @param showCredit
 * @param chartTitle
 * @param creditUrl
 * @returns {JSX.Element}
 * @constructor
 */
const ChartDownloader = ({
	children,
	downloadFileName = 'chart.png',
	imageWidth = 1200,
	showDownloadButton = true,
	showCredit = true,
	chartTitle,
	creditUrl,
}) => {
	const [svgEl, setSvgEl] = useState()

	const downloadImage = () => {
		if (svgEl) {
			// Adjust spacing for title, credits, etc
			const chartTitleOffset = chartTitle ? 48 : 0
			const chartMetaOffset = showCredit ? (creditUrl ? 48 : 24) : 0

			// Calculate the final dimensions of our downloaded image
			const { width: svgWidth, height: svgHeight } = svgEl.getBoundingClientRect()
			const imageHeight = ((svgHeight / svgWidth) * imageWidth)
			const totalImageHeight = imageHeight + chartTitleOffset + chartMetaOffset

			// Create an offscreen canvas for rendering
			const canvas = new OffscreenCanvas(imageWidth, totalImageHeight)
			const ctx = canvas.getContext('2d')

			// Get the SVG as a raw string, and wrap it in another svg that provides
			// the background white, title, logo, and url
			const svgStringData = new XMLSerializer().serializeToString(svgEl)
			const scaledSvgString = `
				<svg
					width="${imageWidth}"
					height="${totalImageHeight}"
					viewBox="0 ${-chartTitleOffset} ${imageWidth} ${totalImageHeight}"
				>
					<rect
						x="0"
						y="${-chartTitleOffset}"
						width="${imageWidth}"
						height="${totalImageHeight}"
						fill="white"
					/>
					<text x="5" y="0" font-size="48">${chartTitle}</text>
					${showCredit ? `
						<text x="5" y="${imageHeight + 14}" font-size="24">
							Source: U.S. Press Freedom Tracker Database
						</text>
						${creditUrl ? `
							<text x="5" y="${imageHeight + 42}" font-size="24" fill="#CCCCCC">
								${creditUrl}
							</text>
						` : ""}
					` : ""}
					<svg width="${imageWidth}" height="${imageHeight}" viewBox="0 0 ${svgWidth} ${svgHeight}">
						${svgStringData}
					</svg>
				</svg>
			`;

			// Render it with canvg
			const canvg = Canvg.fromString(ctx, scaledSvgString)
			canvg.render()
				.then(() => canvas.convertToBlob())
				.then((blob) => {
					// Create and download the blob
					const downloadUrl = URL.createObjectURL(blob)
					const a = document.createElement("a")
					a.href = downloadUrl
					a.download = downloadFileName
					a.click()
					URL.revokeObjectURL(downloadUrl)
				})
		}
	}

	// Clone children with the added data prop and return it
	const chartEl = React.cloneElement(children, { setSvgEl, downloadImage })

	return (
		<>
			{chartEl}
			{showDownloadButton
				? (
					<button className={classNames('btn', 'btn-secondary')} onClick={downloadImage}>
						Download Chart as PNG
					</button>
				)
				: null}
		</>
	)
}

export default ChartDownloader
