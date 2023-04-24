import React from 'react'
import * as d3 from 'd3'
import Renderer from 'react-test-renderer'
import CategoryPageChart from '../CategoryPageChart'

test('renders CategoryPageChart with mocked data', () => {
	expect(Renderer.create(
		<CategoryPageChart
			data={[{ categories: ['test'], date: d3.timeParse("%m-%d-%Y")('1-1-2020') }]}
			category={'test'}
			width={500}
			categoryName={'test'}
		/>
	)).toMatchSnapshot();
});
