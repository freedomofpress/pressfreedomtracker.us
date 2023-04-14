import React from 'react'
import ReactTestRenderer from 'react-test-renderer'
import BarChart from '../BarChart'

test('renders BarChart with mocked data', () => {
	expect(ReactTestRenderer.create(
		<BarChart
			data={[{"month":10,"monthName":"Nov","numberOfIncidents":0},{"month":11,"monthName":"Dec","numberOfIncidents":0},{"month":0,"monthName":"Jan","numberOfIncidents":0},{"month":1,"monthName":"Feb","numberOfIncidents":0},{"month":2,"monthName":"Mar","numberOfIncidents":0},{"month":3,"monthName":"Apr","numberOfIncidents":0}]}
			x="monthName"
			y="numberOfIncidents"
			titleLabel="incidents"
			isMobileView={false}
			width={480}
			height={500}
		/>
	)).toMatchSnapshot();
});
