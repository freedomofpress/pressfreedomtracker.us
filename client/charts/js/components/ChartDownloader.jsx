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

	// Approximate character width based on height
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

			const TITLE_FONT_SIZE = 44
			const PADDING = 10
			const CREDIT_FONT_SIZE = 24

			const titleLineHeight = TITLE_FONT_SIZE * 1.2
			const creditLineHeight = CREDIT_FONT_SIZE * 1.2

			const titleMaxWidth = imageWidth - (PADDING * 2)

			// Wrap the title text
			const titleLines = wrapText(chartTitle, titleMaxWidth, TITLE_FONT_SIZE)
			const numberOfTitleLines = titleLines.length

			// Get element heights and calculate final dimensions
			const titleAreaHeight = chartTitle ? (numberOfTitleLines * titleLineHeight) + PADDING : 0
			const creditAreaHeight = showCredit ?
				(creditUrl ? (creditLineHeight * 2) : creditLineHeight) + PADDING : 0
			const { width: svgWidth, height: svgHeight } = svgEl.getBoundingClientRect()
			const chartImageHeight = ((svgHeight / svgWidth) * imageWidth)
			const totalImageHeight = titleAreaHeight + chartImageHeight + creditAreaHeight

			// Get offset positions
			const titleStartY = titleLineHeight
			const chartStartY = titleAreaHeight
			const creditStartY = titleAreaHeight + chartImageHeight + (creditLineHeight * 0.8) // 0.8 to position at baseline

			// Create an offscreen canvas for rendering
			const canvas = new OffscreenCanvas(imageWidth, totalImageHeight)
			const ctx = canvas.getContext('2d')

			// Generate the title text elements with line breaks
			const titleTextElements = titleLines.map((line, index) => {
				if (index === 0) {
					return `<tspan x="${PADDING}">${escapeXml(line)}</tspan>`
				} else {
					return `<tspan x="${PADDING}" dy="${titleLineHeight}">${escapeXml(line)}</tspan>`
				}
			}).join('\n')

			const svgStringData = new XMLSerializer().serializeToString(svgEl)
			const scaledSvgString = `
				<svg
					width="${imageWidth}"
					height="${totalImageHeight}"
					viewBox="0 0 ${imageWidth} ${totalImageHeight}"
				>
					<rect
						x="0"
						y="0"
						width="${imageWidth}"
						height="${totalImageHeight}"
						fill="white"
					/>
					${chartTitle ? `
					<text x="${PADDING}" y="${titleStartY}" font-size="${TITLE_FONT_SIZE}" >
						${titleTextElements}
					</text>
					` : ""}
					${showCredit ? `
						<text x="${PADDING}" y="${creditStartY}" font-size="${CREDIT_FONT_SIZE}">
							<tspan>Source: U.S. Press Freedom Tracker Database</tspan>
							${creditUrl ? `
								<tspan x="${PADDING}" dy="${creditLineHeight}" fill="#767676">
									${creditUrl}
								</tspan>
							` : ""}
						</text>
					` : ""}
					<svg x="0" y="${chartStartY}" width="${imageWidth}" height="${chartImageHeight}">
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
