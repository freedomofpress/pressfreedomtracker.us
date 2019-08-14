import React from 'react';
import { shallow, mount } from 'enzyme';
import FiltersHeader from '~/filtering/FiltersHeader';
import {
	CATEGORIES_FILTER,
	CATEGORIES_ENABLED,
    FILTER_VALUES
} from '~/tests/factories/CategoriesFilterFactory';

describe('FiltersHeader', () => {
	let categories;
	let categoriesEnabled;
	let filterValues;

    beforeEach(() => {
        categories = CATEGORIES_FILTER;
        categoriesEnabled = CATEGORIES_ENABLED;
        filterValues = FILTER_VALUES;
    });

    afterEach(() => {
        categories = null;
        categoriesEnabled = null;
        filterValues = null;
    });

    it('should render correctly in "debug" mode', () => {
        const component = shallow(
        <FiltersHeader
            categories={categories}
            debug
        />
        );

        expect(component).toMatchSnapshot();
	});

	it('should render FiltersHeader properly with button toggle', () => {
		const component = mount(
        <FiltersHeader
            categories={categories}
            categoriesEnabled={categoriesEnabled}
            filterValues={filterValues}
        />
        );
        const filterButton = component.find('button.filters__button--summary-toggle');
        expect(filterButton.text()).toEqual('Change Filters');
        expect(filterButton.find('svg.filters__icon').length).toEqual(1);
	});

	it('should show FilterSummary properly according to filters', () => {
		const component = mount(
            <FiltersHeader
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
