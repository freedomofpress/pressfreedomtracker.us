import React from 'react'
import ShallowRenderer from 'react-test-renderer/shallow'
import Autocomplete from '../Autocomplete'

test('renders Autocomplete with mocked data', () => {
	const renderer = new ShallowRenderer();
	expect(renderer.render(
		<Autocomplete
			suggestions={[{label: "test label"}]}
			suggestionsLabelField={'label'}
			placeholder={'test'}
			name={'test autocomplete'}
			itemNamePlural={'tests'}
			handleSelect={() => {}}
			suggestionsSidenoteField={'sidenote'}
		/>
	)).toMatchSnapshot();
});
