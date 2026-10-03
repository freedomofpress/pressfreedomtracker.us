import React from "react";
import { render } from "@testing-library/react";
import Button from "../Button";

test("renders Button with mocked data", () => {
	const { container } = render(
		<Button label="test" selected={false} onClick={() => {}} />,
	);
	expect(container).toMatchSnapshot();
});
