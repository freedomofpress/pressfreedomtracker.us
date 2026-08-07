import React from 'react'
import { render } from '@testing-library/react'
import CategorySection from '../CategorySection'

test('renders CategorySection with mocked data', () => {
	const { asFragment } = render(
		<CategorySection symbol="test" label="test" count={2} isOpen={false} onClick={() => {}}>
			This is a test
		</CategorySection>
	)
	expect(asFragment()).toMatchSnapshot()
});
