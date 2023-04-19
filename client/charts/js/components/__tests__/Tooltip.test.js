import React from 'react'
import ReactTestRenderer from 'react-test-renderer'
import Tooltip from '../Tooltip'

jest.mock('react-dom', () => ({
	...jest.requireActual('react-dom'),
	createPortal: node => node
}))

test('renders Tooltip with mocked data', () => {
	expect(ReactTestRenderer.create(
		<Tooltip content="test" x={20} y={20} />
	)).toMatchSnapshot();
});
