import React from 'react'
import * as d3 from 'd3'
import { render } from '@testing-library/react'
import CategoryPageChart from '../CategoryPageChart'

test('renders CategoryPageChart with mocked data', () => {
	const { asFragment } = render(
		<CategoryPageChart
			data={[{ categories: ['test'], date: d3.timeParse("%m-%d-%Y")('1-1-2020') }]}
			category={'test'}
			width={500}
			categoryName={'test'}
		/>
	)
	expect(asFragment()).toMatchSnapshot()
});
