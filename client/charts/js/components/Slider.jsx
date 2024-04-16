import React, { useState, useRef, useEffect } from 'react'
import * as d3 from 'd3'
import { clamp, first, last } from 'lodash'

export default function Slider({ elements, xScale, y, setSliderSelection, sliderSelection, idContainer }) {
	const onSliderReleaseRef = useRef(null)
	const onMouseOrTouchMoveRef = useRef(null)
	const [mousePosition, setMousePosition] = useState({ x: null, y: null })

	useEffect(() => {
		setSliderSelection(first(elements))
	}, [first(elements)])

	function stopMovingSlider(event) {
		window.removeEventListener('mouseup', onSliderReleaseRef.current)
		window.removeEventListener('touchend', onSliderReleaseRef.current)
		onSliderReleaseRef.current = null

		window.removeEventListener('mousemove', onMouseOrTouchMoveRef.current)
		window.removeEventListener('touchmove', onMouseOrTouchMoveRef.current)
		onMouseOrTouchMoveRef.current = null

		setMousePosition({ x: null, y: null })
	}


	function followMouseOrTouch(event) {
		const svg = document.getElementById(idContainer)
		if (svg === null) return

		const dim = svg.getBoundingClientRect()

		let x,y;
		// Mobile
		if (event.type === 'touchmove'){
			const touch = event.touches[0] || event.changedTouches[0];
			x = touch.pageX;
			y = touch.pageY;
		// Desktop
		} else {
			x = event.clientX
			y = event.clientY
		}
		const mouse = { x: x - dim.left, y: y - dim.top }
		setMousePosition(mouse)

		const distancesToMouse = elements.map((d) => ({
			x: d,
			distance: Math.abs(xScale(d) - mouse.x),
		}))
		const selectedValue = distancesToMouse.find(
			(d) => d.distance === d3.min(distancesToMouse.map((e) => e.distance))
		).x
		setSliderSelection(selectedValue)
	}

	return (
		<>
			<line
				x1={xScale(first(elements))}
				x2={xScale(last(elements))}
				y1={y}
				y2={y}
				style={{ strokeWidth: '3px', stroke: 'black' }}
			/>
			{elements.map((d) => (
				<circle
					cx={xScale(d)}
					cy={y}
					r={4}
					style={{
						fill: 'black',
						strokeWidth: 3,
					}}
					onMouseUp={() => setSliderSelection(d)}
					key={d}
				/>
			))}
			<circle
				cx={
					mousePosition.x !== null
						? clamp(mousePosition.x, xScale(first(elements)), xScale(last(elements)))
						: xScale(sliderSelection)
				}
				cy={y}
				r={12}
				style={{ fill: 'white', strokeWidth: 3, stroke: 'black' }}
				onMouseDown={() => {
					window.addEventListener('mouseup', stopMovingSlider)
					onSliderReleaseRef.current = stopMovingSlider

					window.addEventListener('mousemove', followMouseOrTouch)
					onMouseOrTouchMoveRef.current = followMouseOrTouch
				}}
				// Mobile
				onTouchStart={() => {
					window.addEventListener('touchend', stopMovingSlider)
					onSliderReleaseRef.current = stopMovingSlider

					window.addEventListener('touchmove', followMouseOrTouch)
					onMouseOrTouchMoveRef.current = followMouseOrTouch
				}}
			/>
		</>
	)
}
