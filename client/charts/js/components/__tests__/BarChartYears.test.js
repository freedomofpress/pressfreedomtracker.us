import React from 'react'
import ShallowRenderer from 'react-test-renderer/shallow'
import BarChartYears from '../BarChartYears'

test('renders BarChartYears with mocked data', () => {
	const renderer = new ShallowRenderer();
	expect(renderer.render(
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
