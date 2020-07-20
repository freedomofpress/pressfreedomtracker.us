import React from 'react';
import axios from 'axios';
import { shallow, mount } from 'enzyme';
import { AutocompleteInput } from '~/filtering/Inputs';
import Autocomplete from 'WagtailAutocomplete/Autocomplete';
import { TAG_FILTER_VALUES, EMPTY_FILTER_VALUES, TAG_MOCK_RESULTS } from '~/tests/factories/CategoriesFilterFactory';

jest.mock('axios');

// Allows me to ensure that all the promises are resolved.
// setImmediate isn't to be used in production but should
// be fine for testing and CI.
const flushPromises = () => new Promise(setImmediate);

describe('Inputs', () => {

    it('should render AutocompleteInput without error in "debug" mode', () => {
        const component = shallow(
            <AutocompleteInput
                handleFilterChange={jest.fn()}
                filter={'tags'}
                filterValues={EMPTY_FILTER_VALUES}
                label={'Autocomplete'}
                isSingle={false}
                type={'common.CommonTag'}
            />
        );

        expect(component.debug()).toMatchSnapshot();
    });

	it('should render Autocomplete correctly', async () => {
        axios.get.mockImplementationOnce(() => Promise.resolve(
            {
                'data': TAG_MOCK_RESULTS,
                'status': 200
            }
        ));
		const component = mount(
            <AutocompleteInput
                handleFilterChange={jest.fn()}
                filter={'tags'}
                filterValues={EMPTY_FILTER_VALUES}
                label={'Autocomplete'}
                isSingle={false}
                type={'common.CommonTag'}
            />
        )
        await flushPromises();
        component.update();
        const autocompleteComponent = component.find('.autocomplete');
        expect(autocompleteComponent.length).toEqual(1);
        expect(autocompleteComponent.find('.suggestions .suggestions__item').length).toEqual(2);
        component.find('.autocomplete__search').simulate('focus');
        expect(component.find('.suggestions').prop('style')).toHaveProperty('display', 'block');
    });

    it('should render Autocomplete selection results correctly when clicked', async() => {
        axios.get.mockImplementationOnce(() => Promise.resolve(
            {
                'data': TAG_MOCK_RESULTS,
                'status': 200
            }
        ));
		const component = mount(
            <AutocompleteInput
                handleFilterChange={jest.fn()}
                filterValues={EMPTY_FILTER_VALUES}
                label={'Autocomplete'}
                filter={'tags'}
                isSingle={false}
                type={'common.CommonTag'}
            />
        );

        // Mock function to update the props of the root component
        const handleFilterChangeMock = jest.fn((label, event) => {
            component.setProps({filterValues: {[label]: event.target.value}});
        });
        component.setProps({handleFilterChange: handleFilterChangeMock});

        // Used to complete all the promises
        await flushPromises();
        component.update();

        // Before clicking nothing exist
        expect(component.find('.autocomplete-layout__item--padded span').text()).toEqual('Nothing selected.');
        component.find('.autocomplete__search').simulate('focus');

        // Simulate clicking the first option
        const suggestions = component.find('.suggestions .suggestions__item');
        suggestions.first().simulate('click');
        component.update();

        // Check clicking renders the selection
        const selection = component.find('.autocomplete-layout__item--padded .selection');
        expect(selection.length).toEqual(1);
        expect(selection.find('.selection__label').text()).toEqual('Tag 1');

        // Simulate clicking the apply filter button by setting props
        const fetchResult = {
            items: TAG_MOCK_RESULTS.items.filter(result => result.pk === TAG_FILTER_VALUES.tags[0].id),
        }
        axios.get.mockImplementation(() => Promise.resolve(
            {
                'data': fetchResult,
                'status': 200
            }
        ));
        component.setProps({filterValues: TAG_FILTER_VALUES});
        // Used to complete all the promises
        await flushPromises();
        component.update();
        // Check selection still has text
        expect(component.find('.selection .selection__label').text()).toEqual('Tag 1');
    });

    it('should render Autocomplete correctly when filtervalues are there in URL', async () => {
        const fetchResult = {
            items: TAG_MOCK_RESULTS.items.filter(result => result.pk === TAG_FILTER_VALUES.tags[0].id),
        }
        axios.get.mockImplementation((url) => {
            if (url.indexOf('/autocomplete/search/') !== -1) {
                return Promise.resolve(
                    {
                        'data': TAG_MOCK_RESULTS,
                        'status': 200
                    }
                )
            } else if (url.indexOf('/autocomplete/objects/') !== -1) {
                return Promise.resolve(
                    {
                        'data': fetchResult,
                        'status': 200
                    }
                )
            }
        });
		const component = mount(
            <AutocompleteInput
                handleFilterChange={jest.fn()}
                filter={'tags'}
                filterValues={TAG_FILTER_VALUES}
                label={'Autocomplete'}
                isSingle={false}
                type={'common.CommonTag'}
            />
        );
        // Mock function to update the props of the root component
        const handleFilterChangeMock = jest.fn((label, event) => {
            component.setProps({filterValues: {[label]: event.target.value}});
        });
        component.setProps({handleFilterChange: handleFilterChangeMock});

        await flushPromises();
        component.update();
        const selection = component.find('.autocomplete-layout__item--padded .selection');
        expect(selection.length).toEqual(1);
        expect(selection.find('.selection__label').text()).toEqual('Tag 1');
    });
});
