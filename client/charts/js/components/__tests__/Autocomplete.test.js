import React from 'react'
import { render } from '@testing-library/react'
import Autocomplete from '../Autocomplete'

test('renders Autocomplete with mocked data', () => {
	const { asFragment } = render(
		<Autocomplete
			suggestions={[{label: "test label"}]}
			suggestionsLabelField={'label'}
			placeholder={'test'}
			name={'test autocomplete'}
			itemNamePlural={'tests'}
			handleSelect={() => {}}
			suggestionsSidenoteField={'sidenote'}
		/>
	)
	expect(asFragment()).toMatchSnapshot()
});
