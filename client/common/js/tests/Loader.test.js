import React from 'react';
import { shallow, mount } from 'enzyme';
import { HorizontalLoader } from '~/filtering/Loader';

describe('Icons', () => {

    it('should render HorizontalLoader without error in "debug" mode', () => {
        const component = shallow(
            <HorizontalLoader/>
        );

        expect(component.debug()).toMatchSnapshot();
    });

	it('should render HorizontalLoader animation correctly', () => {
		const component = mount(
            <HorizontalLoader/>
        );
        const loaderIcon = component.find('.horizontal-loader');
        expect(loaderIcon.length).toEqual(1);
        expect(loaderIcon.find('span.horizontal-loader__circle').length).toEqual(3);
    });
});