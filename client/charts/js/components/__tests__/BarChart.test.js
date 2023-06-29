import React from 'react'
import ShallowRenderer from 'react-test-renderer/shallow'
import BarChart from '../BarChart'

test('renders BarChart with mocked data', () => {
	const renderer = new ShallowRenderer();
	expect(renderer.render(
		<BarChart
			data={[{"month":10,"monthName":"Nov","numberOfIncidents":0},{"month":11,"monthName":"Dec","numberOfIncidents":0},{"month":0,"monthName":"Jan","numberOfIncidents":0},{"month":1,"monthName":"Feb","numberOfIncidents":0},{"month":2,"monthName":"Mar","numberOfIncidents":0},{"month":3,"monthName":"Apr","numberOfIncidents":0}]}
			x="monthName"
			y="numberOfIncidents"
			titleLabel="incidents"
			isMobileView={false}
			width={480}
			height={500}
			searchPageURL={() => ""}
		/>
	)).toMatchSnapshot();
});
