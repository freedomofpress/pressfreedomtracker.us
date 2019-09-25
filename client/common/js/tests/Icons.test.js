import React from 'react';
import { shallow, mount } from 'enzyme';
import { 
    SettingsIcon,
    ExpandIcon,
    CollapseIcon
} from '~/filtering/Icons';

describe('Icons', () => {

    it('should render SettingsIcon without error in "debug" mode', () => {
        const component = shallow(
            <SettingsIcon/>
        );

        expect(component.debug()).toMatchSnapshot();
    });
    
    it('should render ExpandIcon without error in "debug" mode', () => {
        const component = shallow(
            <ExpandIcon/>
        );

        expect(component.debug()).toMatchSnapshot();
    });
    
    it('should render CollapseIcon without error in "debug" mode', () => {
        const component = shallow(
            <CollapseIcon/>
        );

        expect(component.debug()).toMatchSnapshot();
	});

	it('should render SettingsIcon svg', () => {
		const component = mount(
            <SettingsIcon/>
        );
        const svgIcon = component.find('svg.filters__icon');
		expect(svgIcon.length).toEqual(1);
    });

    it('should render ExpandIcon svg', () => {
		const component = mount(
            <ExpandIcon/>
        );
        const svgIcon = component.find('svg.expand__icon');
		expect(svgIcon.length).toEqual(1);
    });

    it('should render CollapseIcon svg', () => {
		const component = mount(
            <CollapseIcon/>
        );
        const svgIcon = component.find('svg.collapse__icon');
        expect(svgIcon.length).toEqual(1);
        expect(svgIcon.find('title').text()).toEqual('Collapse');
    });
});