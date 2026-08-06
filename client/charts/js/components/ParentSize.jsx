import React from 'react'
import { useParentSize } from '@visx/responsive'

/**
 * Measures available width and hands it to a render-prop child.
 *
 * @visx/responsive's own ParentSize renders children inside a
 * `position: absolute; inset: 0` div, so they contribute no height and any
 * container sized by its content collapses to zero — the charts then render
 * invisibly. This keeps children in normal flow.
 *
 * Height is deliberately neither observed nor exposed: observing the height of
 * the element that holds the children feeds back into the measurement. Every
 * chart here sizes itself from width alone.
 */
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
