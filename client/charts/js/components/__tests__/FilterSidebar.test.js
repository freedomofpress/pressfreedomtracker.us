import React from "react";
import { render } from "@testing-library/react";
import FilterSidebar from "../FilterSidebar";

beforeEach(() => {
	global.fetch = jest.fn(() => new Promise(() => {}));
});

afterEach(() => {
	delete global.fetch;
});

test("renders FilterSidebar with mocked data", () => {
	const { container } = render(
		<FilterSidebar
			initialDataset={[
				{
					date: "2023-02-12T00:00:00.000Z",
					city: "Thomasland",
					state: "ID",
					latitude: null,
					longitude: null,
					categories: "Arrest / Criminal Charge",
					tags: "lemur",
				},
				{
					date: "2022-10-23T00:00:00.000Z",
					city: "New Brooke",
					state: "NC",
					latitude: null,
					longitude: null,
					categories: "Arrest / Criminal Charge",
					tags: "baboon",
				},
				{
					date: "2022-05-12T00:00:00.000Z",
					city: "East Mary",
					state: "CT",
					latitude: null,
					longitude: null,
					categories: "Equipment Search or Seizure",
					tags: "civet",
				},
			]}
			serializedFilters={
				'[{"id": -1, "title": "General", "filters": [{"title": "Search terms", "type": "text", "name": "search"}, {"title": "Took place", "type": "date", "name": "date"}, {"title": "Updated in the last", "type": "int", "name": "recently_updated", "units": "days"}, {"title": "City", "type": "text", "name": "city"}, {"title": "State", "type": "autocomplete", "name": "state", "autocomplete_type": "incident.State", "choices": ["Alaska", "Alabama", "Arkansas", "American Samoa", "Arizona", "California", "Colorado", "Connecticut", "District of Columbia", "Delaware", "Florida", "Georgia", "Guam", "Hawaii", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas"], "many": false}, {"title": "Has any of these tags", "type": "autocomplete", "name": "tags", "autocomplete_type": "common.CommonTag", "choices": ["ammonites", "ants", "aphids", "baboon", "bamboo", "bees", "centipedes"], "many": true}]}, {"id": 4, "title": "Arrest / Criminal Charge", "url": "/arrest-criminal-charge/", "symbol": "arrest", "filters": []}]'
			}
		/>,
	);
	expect(container).toMatchSnapshot();
});
