import React from "react";
import { render } from "@testing-library/react";
import Slider from "../Slider";

test("renders CheckBoxesYear with mocked data", () => {
	const { container } = render(
		<Slider
			elements={["Nov", "Dec", "Jan", "Feb", "Mar", "Apr"]}
			xScale={(x) => x}
			y={400}
			setSliderSelection={() => {}}
			sliderSelection={"Nov"}
			idContainer={"barchart-svg"}
		/>,
	);
	expect(container).toMatchSnapshot();
});
