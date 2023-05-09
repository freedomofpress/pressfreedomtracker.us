import React from 'react'
import * as d3 from 'd3'
import ShallowRenderer from 'react-test-renderer/shallow'
import TimeYearsFilter from '../TimeYearsFilter'

test('renders TimeYearsFilter with mocked data', () => {
	const renderer = new ShallowRenderer();
	expect(renderer.render(
		<TimeYearsFilter
			width={500}
			height={500}
			dateExtents={[d3.timeParse('%m-%d-%Y')('1-1-2020'), d3.timeParse('%m-%d-%Y')('1-1-2022')]}
			dataset={[{ date: d3.timeParse('%m-%d-%Y')('6-1-2020') }]}
			filterParameters={['2020']}
		/>
	)).toMatchSnapshot();
});
