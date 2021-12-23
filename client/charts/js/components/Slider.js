import React, { useState, useRef } from "react";
import * as d3 from "d3";
import { clamp, first, last } from "lodash";

export function Slider({
	elements,
	xScale,
	ycoord,
	setSliderSelection,
	sliderSelection,
	idContainer,
}) {
	const onSliderReleaseRef = useRef(null);
	const onMouseMoveRef = useRef(null);
	const [mousePosition, setMousePosition] = useState({ x: null, y: null });

	if (!elements.includes(sliderSelection) && elements.length > 0) {
		setSliderSelection(first(elements));
	}

	function stopMovingSlider(event) {
		window.removeEventListener("mouseup", onSliderReleaseRef.current);
		onSliderReleaseRef.current = null;

		window.removeEventListener("mousemove", onMouseMoveRef.current);
		onMouseMoveRef.current = null;

		setMousePosition({ x: null, y: null });
	}

	function followMouse(event) {
		const svg = document.getElementById(idContainer);
		if (svg === null) return;

		const dim = svg.getBoundingClientRect();
		const mouse = { x: event.clientX - dim.left, y: event.clientY - dim.top };
		setMousePosition(mouse);

		const distancesToMouse = elements.map((d) => ({
			x: d,
			distance: Math.abs(xScale(d) - mouse.x),
		}));
		const selectedValue = distancesToMouse.find(
			(d) => d.distance === d3.min(distancesToMouse.map((e) => e.distance))
		).x;
		setSliderSelection(selectedValue);
	}

	return (
		<>
			<line
				x1={xScale(first(elements))}
				x2={xScale(last(elements))}
				y1={ycoord}
				y2={ycoord}
				style={{ strokeWidth: "3px", stroke: "black" }}
			/>
			{elements.map((d) => (
				<circle
					cx={xScale(d)}
					cy={ycoord}
					r={4}
					style={{
						fill: "black",
						strokeWidth: 3,
					}}
					onMouseUp={() => setSliderSelection(d)}
					key={d}
				/>
			))}
			<circle
				cx={
					mousePosition.x !== null
						? clamp(
								mousePosition.x,
								xScale(first(elements)),
								xScale(last(elements))
						  )
						: xScale(sliderSelection)
				}
				cy={ycoord}
				r={12}
				style={{ fill: "white", strokeWidth: 3, stroke: "black" }}
				onMouseDown={() => {
					window.addEventListener("mouseup", stopMovingSlider);
					onSliderReleaseRef.current = stopMovingSlider;

					window.addEventListener("mousemove", followMouse);
					onMouseMoveRef.current = followMouse;
				}}
			/>
		</>
	);
}
