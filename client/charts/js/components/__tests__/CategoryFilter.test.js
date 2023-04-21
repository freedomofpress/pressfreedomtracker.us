import React from 'react'
import ShallowRenderer from 'react-test-renderer/shallow'
import CategoryFilter from '../CategoryFilter'

test('renders CategoryFilter with mocked data', () => {
	const renderer = new ShallowRenderer();
	expect(renderer.render(
		<CategoryFilter
			dataset={[{ categories: ['test'] }]}
			filterDefs={[{ title: 'test-def', id: 'test-def', symbol: 'test-def', filters: [] }]}
			filterParameters={{}}
			width={500}
			height={500}
		/>
	)).toMatchSnapshot();
});
