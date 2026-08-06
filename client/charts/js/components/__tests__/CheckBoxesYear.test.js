import React from 'react'
import { render } from '@testing-library/react'
import CheckBoxesYear from '../CheckBoxesYear'

test('renders CheckBoxesYear with mocked data', () => {
	const { asFragment } = render(
		<CheckBoxesYear
			width={500}
			options={[{ year: 2020 }]}
			selectedYears={[2020]}
			onClick={() => {}}
		/>
	)
	expect(asFragment()).toMatchSnapshot()
});
