import React from 'react'
import ReactTestRenderer from 'react-test-renderer'
import ChartDescription from '../ChartDescription'

test('renders ChartDescription with mocked data', () => {
	expect(ReactTestRenderer.create(
		<ChartDescription id="test">
			This is a test
		</ChartDescription>
	)).toMatchSnapshot();
});
