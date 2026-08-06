import React from 'react'
import { render } from '@testing-library/react'
import Tooltip from '../Tooltip'

test('renders Tooltip with mocked data', () => {
	// Tooltip portals into document.body, so it renders outside the container;
	// baseElement covers it.
	const { baseElement } = render(
		<Tooltip content="test" x={20} y={20} />
	)
	expect(baseElement).toMatchSnapshot()
});
