import React from 'react'
import ShallowRenderer from 'react-test-renderer/shallow'
import Button from '../Button'

test('renders Button with mocked data', () => {
	const renderer = new ShallowRenderer();
	expect(renderer.render(
		<Button
			label="test"
			selected={false}
			onClick={() => {}}
		/>
	)).toMatchSnapshot();
});
