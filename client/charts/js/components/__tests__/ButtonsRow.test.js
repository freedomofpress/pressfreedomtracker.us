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

test("selects the dropdown when the default selection is one of its labels", () => {
	const { container } = render(
		<ButtonsRow
			label="test"
			buttonLabels={["test1"]}
			dropDownLabels={[2026, 2025]}
			defaultSelection={2025}
			updateSelection={() => {}}
			isButtonSelectable={() => true}
		/>,
	);
	const select = container.querySelector("select");
	expect(select.value).toBe("2025");
	expect(select.style.backgroundColor).toBe("black");
	expect(container.querySelector("button").style.backgroundColor).not.toBe(
		"black",
	);
});
