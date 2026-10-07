import React from "react";
import { render } from "@testing-library/react";
import CheckBoxBar from "../CheckBoxBar";

test("renders CheckBoxBar with mocked data", () => {
	const { container } = render(
		<CheckBoxBar
			label="test"
			count={2}
			isSelected={false}
			onClick={() => {}}
		/>,
	);
	expect(container).toMatchSnapshot();
});
