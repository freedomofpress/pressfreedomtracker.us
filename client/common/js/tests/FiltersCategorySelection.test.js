import React from 'react';
import { shallow, mount } from 'enzyme';
import FiltersCategorySelection from '~/filtering/FiltersCategorySelection';
import { GENERAL_ID } from '~/filtering/constants'
import {
    CATEGORIES_FILTER,
	CATEGORIES_ENABLED,
} from '~/tests/factories/CategoriesFilterFactory';

describe('FiltersCategorySelection', () => {
    let categories;
	let categoriesEnabled;

    beforeEach(() => {
        categories = CATEGORIES_FILTER;
        categoriesEnabled = CATEGORIES_ENABLED;
    });

    afterEach(() => {
        categories = null;
        categoriesEnabled = null;
    });

    it('should render without error in "debug" mode', () => {
        const component = shallow(
            <FiltersCategorySelection
                categories={categories.filter(({ id }) => id !== GENERAL_ID)}
                categoriesEnabled={categoriesEnabled}
                handleSelection={jest.fn()}
            />
        );

        expect(component.debug()).toMatchSnapshot();
	});

	it('should render FiltersCategorySelection properly with categories values', () => {
		const component = mount(
            <FiltersCategorySelection
                categories={categories.filter(({ id }) => id !== GENERAL_ID)}
                categoriesEnabled={categoriesEnabled}
                handleSelection={jest.fn()}
            />
        );
        const filterCategories = component.find('.filters__category');
        const activeFilterCategory = component.find('.filters__category--active')
        expect(filterCategories.length).toEqual(5);
        expect(activeFilterCategory.length).toEqual(1);
        expect(activeFilterCategory.text()).toEqual('Leak Case');

    });
});