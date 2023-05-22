import React from 'react'
import ShallowRenderer from 'react-test-renderer/shallow'
import TagFilter from '../TagFilter'

test('renders TagFilter with mocked data', () => {
	const renderer = new ShallowRenderer();
	expect(renderer.render(
		<TagFilter
			dataset={[
				{
					"date": "2023-02-12T00:00:00.000Z",
					"city": "Thomasland",
					"state": "ID",
					"latitude": null,
					"longitude": null,
					"categories": [
						"Arrest / Criminal Charge"
					],
					"tags": [
						"lemur"
					]
				},
				{
					"date": "2022-10-23T00:00:00.000Z",
					"city": "New Brooke",
					"state": "NC",
					"latitude": null,
					"longitude": null,
					"categories": [
						"Arrest / Criminal Charge"
					],
					"tags": [
						"baboon"
					]
				},
				{
					"date": "2022-05-12T00:00:00.000Z",
					"city": "East Mary",
					"state": "CT",
					"latitude": null,
					"longitude": null,
					"categories": [
						"Equipment Search or Seizure"
					],
					"tags": [
						"civet"
					]
				}
			]}
			width={200}
			initialPickedTags={new Set()}
			filterParameters={new Set()}
		/>
	)).toMatchSnapshot();
});
