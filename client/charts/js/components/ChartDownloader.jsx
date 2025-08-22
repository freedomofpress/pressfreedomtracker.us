import React, { useState } from 'react'
import classNames from 'classnames'
import { Canvg } from 'canvg'

/**
 * Helper function to wrap text into multiple lines
 * @param text - The text to wrap
 * @param maxWidth - Maximum width in pixels
 * @param fontSize - Font size in pixels
 * @returns {string[]} Array of text lines
 */
const wrapText = (text, maxWidth, fontSize) => {
	if (!text) return []

	// Approximate rough character width based on height
	const avgCharWidth = fontSize * 0.5
	const maxCharsPerLine = Math.floor(maxWidth / avgCharWidth)

	const words = text.split(' ')
	const lines = []
	let currentLine = ''

	for (const word of words) {
		const testLine = currentLine ? `${currentLine} ${word}` : word

		if (testLine.length <= maxCharsPerLine) {
			currentLine = testLine
		} else {
			if (currentLine) {
				lines.push(currentLine)
			}
			currentLine = word
		}
	}

	if (currentLine) {
		lines.push(currentLine)
	}

	return lines
}

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

			const titleFontSize = 48
			const titleLineHeight = titleFontSize * 1.2
			const titleMaxWidth = imageWidth - 10 // 5pt padding

			// Wrap the title text
			const titleLines = wrapText(chartTitle, titleMaxWidth, titleFontSize)
			const numberOfTitleLines = titleLines.length

			// Adjust spacing for title, # of lines, credits, etc
			const chartTitleOffset = chartTitle ? (numberOfTitleLines * titleLineHeight) + 10 : 0
			const chartMetaOffset = showCredit ? (creditUrl ? 48 : 24) : 0

			// Calculate the final dimensions of our downloaded image
			const { width: svgWidth, height: svgHeight } = svgEl.getBoundingClientRect()
			const imageHeight = ((svgHeight / svgWidth) * imageWidth)
			const totalImageHeight = imageHeight + chartTitleOffset + chartMetaOffset

			// Create an offscreen canvas for rendering
			const canvas = new OffscreenCanvas(imageWidth, totalImageHeight)
			const ctx = canvas.getContext('2d')

			// Generate the title text elements with line breaks
			const titleTextElements = titleLines.map((line, index) => {
				// Start from the top of the viewBox (which is -chartTitleOffset)
				// and work our way down
				const yPosition = -chartTitleOffset + ((index + 1) * titleLineHeight) - 10
				return `<text x="5" y="${yPosition}" font-size="${titleFontSize}">${escapeXml(line)}</text>`
			}).join('\n')

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
					${chartTitle ? titleTextElements : ''}
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
					<svg width="${imageWidth}" height="${imageHeight}">
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

	// Escape text for safe use in SVG with browser textContent escaping
	const escapeXml = (text) => {
		if (!text) return ''
		const div = document.createElement('div')
		div.textContent = text
		return div.innerHTML
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
