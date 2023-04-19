import React from 'react'
import ReactTestRenderer from 'react-test-renderer'
import BarChartYears from '../BarChartYears'

test('renders BarChartYears with mocked data', () => {
	expect(ReactTestRenderer.create(
		<BarChartYears
			countYears={[{"year":2012,"count":2,"numberOfIncidents":0}]}
			x="monthName"
			y="numberOfIncidents"
			selectedYears={[2012]}
			width={480}
			height={500}
		/>
	)).toMatchSnapshot();
});
