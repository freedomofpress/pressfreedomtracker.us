import React from "react";
import { render } from "@testing-library/react";
import Tooltip from "../Tooltip";

test("renders Tooltip with mocked data", () => {
	render(<Tooltip content="test" x={20} y={20} />);
	expect(document.body).toMatchSnapshot();
});
