import React from 'react';
import { shallow, mount } from 'enzyme';
import FiltersExpandable from '~/filtering/FiltersExpandable';
import {
    FILTERS_EXPANDED
} from '~/tests/factories/CategoriesFilterFactory';

describe('FiltersExpandable', () => {
    let filtersExpanded;

    beforeEach(() => {
        filtersExpanded = FILTERS_EXPANDED;
    });

    afterEach(() => {
        filtersExpanded = null;
    });

    it('should render without error in "debug" mode', () => {
        const component = shallow(
            <FiltersExpandable
                filtersExpanded={filtersExpanded}
            />
        );

        expect(component.debug()).toMatchSnapshot();
	});

	it('should render FiltersExpandable properly with filtersExpanded values', () => {
		const component = mount(
            <FiltersExpandable
                filtersExpanded={filtersExpanded}
            />
        );
        let expandedFilter = component.find('.filters__expandable.filters__expandable--expanded');
        expect(expandedFilter.length).toEqual(1);

        const unexpandedComponent = mount(
            <FiltersExpandable
                filtersExpanded={!filtersExpanded}
            />
        );
        expandedFilter = unexpandedComponent.find('.filters__expandable.filters__expandable--expanded');
        expect(expandedFilter.length).toEqual(0);
    });
});