import React from 'react'
import ShallowRenderer from 'react-test-renderer/shallow'
import CheckBoxesYear from '../CheckBoxesYear'

test('renders CheckBoxesYear with mocked data', () => {
	const renderer = new ShallowRenderer();
	expect(renderer.render(
		<CheckBoxesYear
			width={500}
			options={[{ year: 2020 }]}
			selectedYears={[2020]}
			onClick={() => {}}
		/>
	)).toMatchSnapshot();
});
