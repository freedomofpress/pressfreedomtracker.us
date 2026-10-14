import React from "react";
import { render } from "@testing-library/react";
import ChartDescription from "../ChartDescription";

test("renders ChartDescription with mocked data", () => {
	const { container } = render(
		<ChartDescription id="test">This is a test</ChartDescription>,
	);
	expect(container).toMatchSnapshot();
});
