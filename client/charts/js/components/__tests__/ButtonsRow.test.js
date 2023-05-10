import React from 'react'
import ShallowRenderer from 'react-test-renderer/shallow'
import ButtonsRow from '../ButtonsRow'

test('renders ButtonsRow with mocked data', () => {
	const renderer = new ShallowRenderer();
	expect(renderer.render(
		<ButtonsRow
			label="test"
			buttonLabels={['test1', 'test2']}
			updateSelection={() => {}}
			isButtonSelectable={() => true}
		/>
	)).toMatchSnapshot();
});
