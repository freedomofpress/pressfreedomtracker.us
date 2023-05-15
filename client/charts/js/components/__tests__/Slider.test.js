import React from 'react'
import ShallowRenderer from 'react-test-renderer/shallow'
import Slider from '../Slider'

test('renders CheckBoxesYear with mocked data', () => {
	const renderer = new ShallowRenderer();
	expect(renderer.render(
		<Slider
			elements={["Nov", "Dec", "Jan", "Feb", "Mar", "Apr"]}
			xScale={(x) => x}
			y={400}
			sliderSelection={'Nov'}
			idContainer={'barchart-svg'}
		/>
	)).toMatchSnapshot();
});
