import React from 'react'
import { render } from '@testing-library/react'
import Slider from '../Slider'

test('renders CheckBoxesYear with mocked data', () => {
	const { asFragment } = render(
		<Slider
			elements={["Nov", "Dec", "Jan", "Feb", "Mar", "Apr"]}
			xScale={(x) => x}
			y={400}
			sliderSelection={'Nov'}
			setSliderSelection={() => {}}
			idContainer={'barchart-svg'}
		/>
	)
	expect(asFragment()).toMatchSnapshot()
});
