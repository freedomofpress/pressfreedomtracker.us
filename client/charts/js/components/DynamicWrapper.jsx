import React from 'react'

/**
 * DynamicWrapper allows for elements to be allowed to conditionally wrap, based on
 * whether the wrap prop is true or false.
 *
 * @param wrap
 * @param children
 * @param wrapperComponent
 * @returns {React.DetailedReactHTMLElement<{}, HTMLElement>|*}
 * @constructor
 */
export default function DynamicWrapper({ wrap = true, children, wrapperComponent }) {
	if (wrap && wrapperComponent) return React.cloneElement(wrapperComponent, {}, children)
	else return children
}
