import React from 'react'
import { render } from '@testing-library/react'
import CategoryFilter from '../CategoryFilter'

test('renders CategoryFilter with mocked data', () => {
	const { asFragment } = render(
		<CategoryFilter
			dataset={[{ categories: ['test'] }]}
			filterDefs={[{ title: 'test-def', id: 'test-def', symbol: 'test-def', filters: [] }]}
			filterParameters={{}}
			width={500}
			height={500}
		/>
	)
	expect(asFragment()).toMatchSnapshot()
});
