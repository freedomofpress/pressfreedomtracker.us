import React from 'react';
import { shallow, mount } from 'enzyme';
import FiltersFooter from '~/filtering/FiltersFooter';
import {
	CATEGORIES_FILTER,
	PAGE_FETCH_PARAMS
} from '~/tests/factories/CategoriesFilterFactory';

describe('FiltersFooter', () => {
	let categories;
	let pageFetchParams;

	beforeEach(() => {
		categories = CATEGORIES_FILTER;
		pageFetchParams = PAGE_FETCH_PARAMS;
	});

	afterEach(() => {
		categories = null;
		pageFetchParams = null;
	});

	it('should render without error in "debug" mode', () => {
		const component = shallow(
		<FiltersFooter
			categories={categories}
		/>
		);

		expect(component.debug()).toMatchSnapshot();
	});

	it('should render the correct export link without param', () => {
		const component = mount(
			<FiltersFooter
				categories={categories}
				exportPath={'test-path/'}
			/>
		);

		// Check the download link is rendered properly
		expect(component.find('a.filters__link').length).toEqual(1);
		expect(component.find('a.filters__link').text()).toEqual('Download the Data.');
		expect(component.find('a.filters__link').filterWhere((item) => {
			return item.prop('href') === 'test-path/export/?'
		}).length).toEqual(1);
	});

	it('should render the correct export link with param', () => {
		const component = mount(
			<FiltersFooter
				categories={categories}
				exportPath={'test-path/'}
				pageFetchParams={pageFetchParams}
			/>
		);

		// Check the download link is rendered properly
		expect(component.find('a.filters__link').length).toEqual(1);
		expect(component.find('a.filters__link').text()).toEqual('Download the Data.');
		expect(component.find('a.filters__link').filterWhere((item) => {
			return item.prop('href') === 'test-path/export/?categories=5&charged_under_espionage_act=True'
		}).length).toEqual(1);
	});

	it('should render filter footer buttons properly ', () => {
		const component = mount(
			<FiltersFooter
				categories={categories}
				loading={0}
			/>
		);

		expect(component.find('.horizontal-loader').length).toEqual(0);

		//Check 2 filter buttons exist
		expect(component.find('button.filters__button').length).toEqual(2);

		// Check the clear button exists and it's type is button
		expect(component.find('button.filters__button').filterWhere((item) => {
			return item.prop('type') === 'button'
		}).length).toEqual(1);
		expect(component.find('button.filters__button').filterWhere((item) => {
			return item.prop('type') === 'button'
		}).text()).toEqual('Clear Filters');

		// Check the apply button exists and it's type is submit and it is bordered
		expect(component.find('button.filters__button--bordered').filterWhere((item) => {
			return item.prop('type') === 'submit'
		}).length).toEqual(1);
		expect(component.find('button.filters__button--bordered').filterWhere((item) => {
			return item.prop('type') === 'submit'
		}).text()).toEqual('Apply Filters');
	});

	it('should render filter footer buttons properly ', () => {
		const component = mount(
			<FiltersFooter
				categories={categories}
				loading={1}
			/>
		);
		expect(component.find('.horizontal-loader').length).toEqual(1);
	});
});
