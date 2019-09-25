import React from 'react';
import { shallow, mount } from 'enzyme';
import FilterSet from '~/filtering/FilterSet';
import { GENERAL_ID } from '~/filtering/constants'
import {
    CATEGORIES_FILTER,
	FILTER_VALUES,
} from '~/tests/factories/CategoriesFilterFactory';

describe('FilterSet', () => {
    let categories;
	let filterValues;

    beforeEach(() => {
        categories = CATEGORIES_FILTER;
        filterValues = FILTER_VALUES;
    });

    afterEach(() => {
        categories = null;
        filterValues = null;
    });

    it('should render without error in "debug" mode', () => {
        const component = shallow(
            <FilterSet
                filters={categories[0].filters}
                handleFilterChange={jest.fn()}
                filterValues={filterValues}
            />
        );

        expect(component.debug()).toMatchSnapshot();
	});

	it('should render FilterSet properly with categories values', () => {
		const component = mount(
            <FilterSet
                filters={categories[0].filters}
                handleFilterChange={jest.fn()}
                filterValues={filterValues}
            />
        );
        const filterSets = component.find('.filters__set');
        expect(filterSets.find('.filter-text-input').length).toEqual(1);
        expect(filterSets.find('.filters__date-picker').length).toEqual(2);
    });
});