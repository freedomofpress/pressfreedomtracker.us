import React from 'react'
import ShallowRenderer from 'react-test-renderer/shallow'
import CheckBoxBar from '../CheckBoxBar'

test('renders CheckBoxBar with mocked data', () => {
	const renderer = new ShallowRenderer();
	expect(renderer.render(
		<CheckBoxBar
			label="test"
			count={2}
			isSelected={false}
			onClick={() => {}}
		/>
	)).toMatchSnapshot();
});
