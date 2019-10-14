import React from 'react';
import { shallow, mount } from 'enzyme';
import CategoryList from '~/filtering/CategoryList';
import {
	CATEGORIES_FILTER,
	CATEGORIES_ENABLED,
    FILTER_VALUES,
} from '~/tests/factories/CategoriesFilterFactory';

describe('CategoryList', () => {
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
            <CategoryList
                categories={categories.filter(({ id }) => categoriesEnabled[id])}
            />
        );

        expect(component.debug()).toMatchSnapshot();
	});

	it('should render CategoryList properly with data', () => {
		const component = mount(
            <CategoryList
                categories={categories.filter(({ id }) => categoriesEnabled[id])}
            />
        );
        const categoryList = component.find('.filters__summary-item');
		expect(categoryList.text()).toEqual(
			'Leak Case'
		);
    });
});