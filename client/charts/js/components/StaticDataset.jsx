import React from 'react'

/**
 * Static version of React Animated Dataset used for server-side rendering
 *
 * @param dataset
 * @param tag
 * @param attrs
 * @param keyFn
 * @param children
 * @returns {JSX.Element}
 * @constructor
 */
export default function StaticDataset({ dataset, tag, attrs, keyFn, children }) {
	const attrsList = Object.keys(attrs).filter(a => a !== 'text')

	const items = dataset.map(data => React.createElement(
		tag,
		{
			key: keyFn(data),
			...attrsList.reduce((acc, val) => ({
				...acc,
				[val]: typeof attrs[val] === "function" ? attrs[val](data) : attrs[val]
			}), {})
		},
		// Clone children and assign dataset
		(children && React.Children.toArray(children)
			.map(child => React.cloneElement(child, { key: child.toString(), dataset: [data] })))
		// Or if the child should be text
		|| (attrs.text && typeof attrs.text === "function" ? attrs.text(data) : attrs.text)
	))

	return (<g>{items}</g>)
}
