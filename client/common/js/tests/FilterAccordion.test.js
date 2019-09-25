import React from 'react';
import { shallow, mount } from 'enzyme';
import FilterAccordion from '~/filtering/FilterAccordion';
import {
    CATEGORIES_FILTER,
	FILTER_VALUES,
} from '~/tests/factories/CategoriesFilterFactory';

describe('FilterAccordion', () => {
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
            <FilterAccordion
                category={categories[0]}
                collapsible={true}
                handleFilterChange={jest.fn()}
                filterValues={filterValues}
                startExpanded={true}
            />
        );

        expect(component.debug()).toMatchSnapshot();
	});

	it('should render FilterAccordion properly with collapsible', () => {
		const component = mount(
            <FilterAccordion
                category={categories[0]}
                collapsible={true}
                handleFilterChange={jest.fn()}
                filterValues={filterValues}
                startExpanded={false}
            />
        );
        let filterAccordion = component.find('.filters__accordion');
        expect(filterAccordion.length).toEqual(1);
        expect(filterAccordion.find('.expand__icon').length).toEqual(1);

        const nonCollapsibleComponent = mount(
            <FilterAccordion
                category={categories[0]}
                collapsible={false}
                handleFilterChange={jest.fn()}
                filterValues={filterValues}
                startExpanded={false}
            />
        );
        filterAccordion = nonCollapsibleComponent.find('.filters__accordion');
        expect(filterAccordion.length).toEqual(0);

        const collapsibleExpandedComponent = mount(
            <FilterAccordion
                category={categories[0]}
                collapsible={true}
                handleFilterChange={jest.fn()}
                filterValues={filterValues}
                startExpanded={true}
            />
        );
        filterAccordion = collapsibleExpandedComponent.find('.filters__accordion');
        expect(filterAccordion.find('.collapse__icon').length).toEqual(1);
    });

    it('should render FilterAccordion properly with expanded', () => {
		const component = mount(
            <FilterAccordion
                category={categories[0]}
                collapsible={false}
                handleFilterChange={jest.fn()}
                filterValues={filterValues}
                startExpanded={true}
            />
        );
        const filterAccordion = component.find('.filters__set');
        expect(filterAccordion.length).toEqual(1);
    });
});