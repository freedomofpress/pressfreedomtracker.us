import React from 'react'
import { render } from '@testing-library/react'
import CheckBoxBar from '../CheckBoxBar'

test('renders CheckBoxBar with mocked data', () => {
	const { asFragment } = render(
		<CheckBoxBar
			label="test"
			count={2}
			isSelected={false}
			onClick={() => {}}
		/>
	)
	expect(asFragment()).toMatchSnapshot()
});
