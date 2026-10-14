import React from "react";
import { render } from "@testing-library/react";
import Flashing from "../Flashing";

test("renders Flashing true", () => {
	const { container } = render(<Flashing flashing>test</Flashing>);
	expect(container).toMatchSnapshot();
});

test("renders Flashing false", () => {
	const { container } = render(<Flashing flashing={false}>test</Flashing>);
	expect(container).toMatchSnapshot();
});
