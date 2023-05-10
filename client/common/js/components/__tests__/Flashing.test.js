/* eslint-disable no-undef,react/jsx-filename-extension */
import React from 'react'
import ShallowRenderer from 'react-test-renderer/shallow'
import Flashing from '../Flashing'

test('renders Flashing true', () => {
	const renderer = new ShallowRenderer()
	expect(renderer.render(
		<Flashing flashing>
			test
		</Flashing>,
	)).toMatchSnapshot()
})

test('renders Flashing false', () => {
	const renderer = new ShallowRenderer()
	expect(renderer.render(
		<Flashing flashing={false}>
			test
		</Flashing>,
	)).toMatchSnapshot()
})
