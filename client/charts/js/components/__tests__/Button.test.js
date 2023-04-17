import React from 'react'
import ReactTestRenderer from 'react-test-renderer'
import Button from '../Button'

test('renders Button with mocked data', () => {
	expect(ReactTestRenderer.create(
		<Button
			label="test"
			selected={false}
			onClick={() => {}}
		/>
	)).toMatchSnapshot();
});
