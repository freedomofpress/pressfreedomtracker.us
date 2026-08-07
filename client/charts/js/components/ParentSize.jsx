import React from 'react'
import { useParentSize } from '@visx/responsive'

// @visx/responsive's own ParentSize positions children absolutely, which
// collapses any content-sized container to zero height.
//
// Height is deliberately not observed: this div wraps the children, so
// measuring its height would feed back into the measurement.
const IGNORED_DIMENSIONS = ['height', 'top', 'left']

export default function ParentSize({ children, debounceTime = 300, ...rest }) {
	const { parentRef, width } = useParentSize({
		debounceTime,
		ignoreDimensions: IGNORED_DIMENSIONS,
	})

	return (
		<div ref={parentRef} style={{ width: '100%' }} {...rest}>
			{children({ width })}
		</div>
	)
}
