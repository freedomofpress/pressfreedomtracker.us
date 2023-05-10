import React from 'react'
import ShallowRenderer from 'react-test-renderer/shallow'
import ChartDescription from '../ChartDescription'

test('renders ChartDescription with mocked data', () => {
	const renderer = new ShallowRenderer();
	expect(renderer.render(
		<ChartDescription id="test">
			This is a test
		</ChartDescription>
	)).toMatchSnapshot();
});
