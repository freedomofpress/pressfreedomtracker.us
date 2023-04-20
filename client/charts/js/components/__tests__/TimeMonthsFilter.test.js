import React from 'react'
import ReactTestRenderer from 'react-test-renderer'
import TimeMonthsFilter from '../TimeMonthsFilter'
import * as d3 from 'd3'

test('renders TimeMonthsFilter with mocked data', () => {
	expect(ReactTestRenderer.create(
		<TimeMonthsFilter
			width={500}
			height={500}
			dateExtents={[d3.timeParse('%m-%d-%Y')('1-1-2020'), d3.timeParse('%m-%d-%Y')('1-1-2022')]}
			dataset={[{ date: d3.timeParse('%m-%d-%Y')('6-1-2020') }]}
			filterParameters={{
				min: d3.timeParse('%m-%d-%Y')('1-1-2020'),
				max: d3.timeParse('%m-%d-%Y')('1-1-2022')
			}}
		/>
	)).toMatchSnapshot();
});
