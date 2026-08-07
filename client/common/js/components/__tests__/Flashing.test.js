
import React from 'react'
import { render } from '@testing-library/react'
import Flashing from '../Flashing'

test('renders Flashing true', () => {
	const { asFragment } = render(
		<Flashing flashing>
			test
		</Flashing>,
	)
	expect(asFragment()).toMatchSnapshot()
})

test('renders Flashing false', () => {
	const { asFragment } = render(
		<Flashing flashing={false}>
			test
		</Flashing>,
	)
	expect(asFragment()).toMatchSnapshot()
})
