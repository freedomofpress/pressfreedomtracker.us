import React from 'react';
import { shallow, mount } from 'enzyme';
import FilterSummary from '~/filtering/FilterSummary';
import {
	CATEGORIES_FILTER,
	CATEGORIES_ENABLED,
    FILTER_VALUES,
	EMPTY_CATEGORIES_ENABLED,
    EMPTY_FILTER_VALUES,
    FILTERS_EXPANDED
} from '~/tests/factories/CategoriesFilterFactory';

describe('FilterSummary', () => {
	let categories;
	let categoriesEnabled;
    let filterValues;
    let filtersExpanded;

    beforeEach(() => {
        categories = CATEGORIES_FILTER;
        categoriesEnabled = CATEGORIES_ENABLED;
        filterValues = FILTER_VALUES;
        filtersExpanded = FILTERS_EXPANDED;
    });

    afterEach(() => {
        categories = null;
        categoriesEnabled = null;
        filterValues = null;
        filtersExpanded = null;
    });

    it('should render without error in "debug" mode', () => {
        const component = shallow(
            <FilterSummary
                categories={categories}
                categoriesEnabled={categoriesEnabled}
                filterValues={filterValues}
            />
        );

        expect(component.debug()).toMatchSnapshot();
	});

	it('should render FiltersSummary properly with no filters', () => {
		const component = mount(
            <FilterSummary
                categories={categories}
                categoriesEnabled={EMPTY_CATEGORIES_ENABLED}
                filterValues={EMPTY_FILTER_VALUES}
            />
        );
        const filterSummaryText = component.find('.filters__summary.filters__text--dim');
        expect(filterSummaryText.text()).toEqual('No filters applied.');
    });
    
    it('should render FiltersSummary properly with filtersExpanded', () => {
		const component = mount(
            <FilterSummary
                categories={categories}
                categoriesEnabled={categoriesEnabled}
                filtersExpanded={filtersExpanded}
                filterValues={EMPTY_FILTER_VALUES}
            />
        );
        const filterSummaryText = component.find('.filters__summary');
        expect(filterSummaryText.text()).toEqual('Filters');
	});

	it('should show FilterSummary properly according to filters', () => {
		const component = mount(
            <FilterSummary
                categories={categories}
                categoriesEnabled={categoriesEnabled}
                filterValues={filterValues}
            />
		);
		const filterSummary = component.find('div.filters__summary');
		// 1 Category List, 1 Filter List = 2 List
		expect(filterSummary.find('ul.filters__summary-list').length).toEqual(2);
		expect(filterSummary.find('div.filters__text--dim').text()).toEqual(
			'Showing Leak Case Charged under espionage act?: Yes'
		);
	});
});