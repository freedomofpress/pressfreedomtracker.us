import React from 'react';
import { shallow, mount } from 'enzyme';
import FiltersList from '~/filtering/FiltersList';
import {
    CATEGORIES_FILTER,
    FILTER_VALUES,
    BOOL_FILTER_VALUES,
    DATE_FILTER_VALUES,
    CHOICE_FILTER_VALUES,
    INT_FILTER_VALUES,
} from '~/tests/factories/CategoriesFilterFactory';

describe('FiltersList', () => {
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
            <FiltersList
                categories={categories}
                filterValues={filterValues}
            />
        );

        expect(component.debug()).toMatchSnapshot();
    });

    it('should render FiltersList properly with Boolean type', () => {
        const component = mount(
            <FiltersList
                categories={categories}
                filterValues={BOOL_FILTER_VALUES}
            />
        );
        const filterList = component.find('.filters__summary-item');
        expect(filterList.text()).toEqual(
            'Charged under espionage act?: Yes'
        );
    });

    it('should render FiltersList properly with Date type', () => {
        const component = mount(
            <FiltersList
                categories={categories}
                filterValues={DATE_FILTER_VALUES}
            />
        );
        const filterList = component.find('.filters__summary-item');
        expect(filterList.text()).toEqual(
            'Took place between: Sep 25th 2019 – Sep 26th 2019'
        );
    });

    it('should render FiltersList properly with Choices type', () => {
        const component = mount(
            <FiltersList
                categories={categories}
                filterValues={CHOICE_FILTER_VALUES}
            />
        );
        const filterList = component.find('.filters__summary-item');
        expect(filterList.text()).toEqual(
            'Status of prior restraint: pending'
        );
    });

    it('should render FiltersList properly with Int type', () => {
        const component = mount(
            <FiltersList
                categories={categories}
                filterValues={INT_FILTER_VALUES}
            />
        );
        const filterList = component.find('.filters__summary-item');
        expect(filterList.text()).toEqual(
            `Updated in the last: ${INT_FILTER_VALUES['recently_updated']} days`
        );
    });
});
