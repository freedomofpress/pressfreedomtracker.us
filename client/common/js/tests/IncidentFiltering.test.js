import React from 'react';
import { shallow, mount } from 'enzyme';
import IncidentFiltering from '~/filtering/IncidentFiltering';
import { CATEGORIES_FILTER } from '~/tests/factories/CategoriesFilterFactory';

describe('IncidentFiltering', () => {
	let categories;

	beforeEach(() => {
		categories = CATEGORIES_FILTER;
	});

	afterEach(() => {
		categories = null;
	});

	it('should render without error in "debug" mode', () => {
		const component = shallow(
			<IncidentFiltering
				categories={categories}
			/>
		);

		expect(component.debug()).toMatchSnapshot();
	});

	it('should render FiltersHeader properly with button toggle', () => {
		const component = mount(
			<IncidentFiltering
				categories={categories}
			/>
		);
		const filterButton = component.find('button.filters__button--summary-toggle');
		expect(filterButton.text()).toEqual('Change Filters');
		filterButton.simulate('click');
		expect(filterButton.text()).toEqual('Collapse Filters');
	});

	it('should expand modal when the expand button is clicked', () => {
		const component = mount(
			<IncidentFiltering
				categories={categories}
			/>
		);
		const filterButton = component.find('button.filters__button--summary-toggle');
		expect(component.find('div.filters__expandable--expanded').length).toEqual(0);
		filterButton.simulate('click');
		expect(component.find('div.filters__expandable--expanded').length).toEqual(1);
	});

  	it('should render filter footer properly in filter modal', () => {
    	const component = mount(
			<IncidentFiltering
				categories={categories}
				exportPath={'test-path/'}
			/>
		);
    	const filterButton = component.find('button.filters__button--summary-toggle');
		filterButton.simulate('click');
		const filterFooter = component.find('div.filters__footer');

		// Check the download link is rendered properly
		expect(filterFooter.find('a.filters__link').length).toEqual(1);
		expect(filterFooter.find('a.filters__link').text()).toEqual('Download the Data.');
		expect(filterFooter.find('a.filters__link').filterWhere((item) => {
			return item.prop('href') === 'test-path/export/?'
		}).length).toEqual(1);

		//Check 2 filter buttons exist
		expect(filterFooter.find('button.filters__button').length).toEqual(2);

		// Check the clear button exists and it's type is button
		expect(filterFooter.find('button.filters__button').filterWhere((item) => {
			return item.prop('type') === 'button'
		}).length).toEqual(1);
		expect(filterFooter.find('button.filters__button').filterWhere((item) => {
			return item.prop('type') === 'button'
		}).text()).toEqual('Clear Filters');

		// Check the apply button exists and it's type is submit and it is bordered
		expect(filterFooter.find('button.filters__button--bordered').filterWhere((item) => {
			return item.prop('type') === 'submit'
		}).length).toEqual(1);
		expect(filterFooter.find('button.filters__button--bordered').filterWhere((item) => {
			return item.prop('type') === 'submit'
		}).text()).toEqual('Apply Filters');
	});
});
