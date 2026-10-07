import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import FilterSidebar from "../FilterSidebar";

// Same columns and date format as /api/edge/incidents/homepage_csv/
const homepageCsv = `date,city,state,latitude,longitude,categories,tags
2023-02-12,Thomasland,ID,,,Arrest / Criminal Charge,lemur
2022-10-23,New Brooke,NC,,,Arrest / Criminal Charge,baboon
2022-05-12,East Mary,CT,,,Equipment Search or Seizure,civet`;

beforeEach(() => {
	globalThis.fetch = jest.fn(() =>
		Promise.resolve({ text: () => Promise.resolve(homepageCsv) }),
	);
});

afterEach(() => {
	delete globalThis.fetch;
});

test("renders FilterSidebar with mocked data", async () => {
	const { container } = render(
		<FilterSidebar
			serializedFilters={
				'[{"id": -1, "title": "General", "filters": [{"title": "Search terms", "type": "text", "name": "search"}, {"title": "Took place", "type": "date", "name": "date"}, {"title": "Updated in the last", "type": "int", "name": "recently_updated", "units": "days"}, {"title": "City", "type": "text", "name": "city"}, {"title": "State", "type": "autocomplete", "name": "state", "autocomplete_type": "incident.State", "choices": ["Alaska", "Alabama", "Arkansas", "American Samoa", "Arizona", "California", "Colorado", "Connecticut", "District of Columbia", "Delaware", "Florida", "Georgia", "Guam", "Hawaii", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas"], "many": false}, {"title": "Has any of these tags", "type": "autocomplete", "name": "tags", "autocomplete_type": "common.CommonTag", "choices": ["ammonites", "ants", "aphids", "baboon", "bamboo", "bees", "centipedes"], "many": true}]}, {"id": 4, "title": "Arrest / Criminal Charge", "url": "/arrest-criminal-charge/", "symbol": "arrest", "filters": []}]'
			}
		/>,
	);
	await waitFor(() => expect(screen.queryByText("LOADING...")).toBeNull());
	expect(globalThis.fetch).toHaveBeenCalledWith(
		"/api/edge/incidents/homepage_csv/",
	);
	expect(container).toMatchSnapshot();
});
