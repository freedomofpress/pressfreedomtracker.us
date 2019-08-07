import React from 'react';
import { shallow } from 'enzyme';
import IncidentFiltering from './IncidentFiltering';

describe('IncidentFiltering', () => {
  it('should render correctly in "debug" mode', () => {
    const categories = [
      {
        'id': -1,
        'title': 'General',
        'filters': [],
      }
    ]
    const component = shallow(
      <IncidentFiltering
        categories={categories}
        debug 
      />
    );
  
    expect(component).toMatchSnapshot();
  });
});

describe('Addition', () => {
  it('knows that 2 and 2 make 4', () => {
    expect(2 + 2).toBe(4);
  });
});