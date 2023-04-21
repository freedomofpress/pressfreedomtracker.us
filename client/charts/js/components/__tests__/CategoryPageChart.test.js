import React from 'react'
import ShallowRenderer from 'react-test-renderer/shallow'
import CategoryPageChart from '../CategoryPageChart'

test('renders CategoryPageChart with mocked data', () => {
	const renderer = new ShallowRenderer();
	expect(renderer.render(
		<CategoryPageChart
			dataset={[{ categories: ['test'] }]}
			category={'test'}
			width={500}
			categoryName={'test'}
		/>
	)).toMatchSnapshot();
});
