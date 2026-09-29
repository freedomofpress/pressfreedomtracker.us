import React from "react";
import { render } from "@testing-library/react";
import ButtonsRow from "../ButtonsRow";

test("renders ButtonsRow with mocked data", () => {
	const { container } = render(
		<ButtonsRow
			label="test"
			buttonLabels={["test1", "test2"]}
			updateSelection={() => {}}
			isButtonSelectable={() => true}
		/>,
	);
	expect(container).toMatchSnapshot();
});
