import React from 'react'
import ShallowRenderer from 'react-test-renderer/shallow'
import CategorySection from '../CategorySection'

test('renders CategorySection with mocked data', () => {
	const renderer = new ShallowRenderer();
	expect(renderer.render(
		<CategorySection symbol="test" label="test" count={2} isOpen={false} onClick={() => {}}>
			This is a test
		</CategorySection>
	)).toMatchSnapshot();
});
