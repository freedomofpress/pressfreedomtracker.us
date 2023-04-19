import React from 'react'
import ReactTestRenderer from 'react-test-renderer'
import CategorySection from '../CategorySection'

test('renders CategorySection with mocked data', () => {
	expect(ReactTestRenderer.create(
		<CategorySection symbol="test" label="test" count={2} isOpen={false} onClick={() => {}}>
			This is a test
		</CategorySection>
	)).toMatchSnapshot();
});
