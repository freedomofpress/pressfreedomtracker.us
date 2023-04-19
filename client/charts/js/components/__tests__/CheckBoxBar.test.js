import React from 'react'
import ReactTestRenderer from 'react-test-renderer'
import CheckBoxBar from '../CheckBoxBar'

test('renders CheckBoxBar with mocked data', () => {
	expect(ReactTestRenderer.create(
		<CheckBoxBar
			label="test"
			count={2}
			isSelected={false}
			onClick={() => {}}
		/>
	)).toMatchSnapshot();
});
