import React from 'react'
import ShallowRenderer from 'react-test-renderer/shallow'
import Tooltip from '../Tooltip'

test('renders Tooltip with mocked data', () => {
	const renderer = new ShallowRenderer();
	expect(renderer.render(
		<Tooltip content="test" x={20} y={20} />
	)).toMatchSnapshot();
});
