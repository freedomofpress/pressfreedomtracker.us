import React, { PureComponent } from 'react'
import {
  AutocompleteInput,
  BoolInput,
  ChoiceInput,
  DateRangeInput,
  TextInput,
  RadioPillInput,
} from '~/filtering/Inputs'

import { AUTOCOMPLETE_SINGLE_FILTERS, AUTOCOMPLETE_MULTI_FILTERS } from '~/filtering/constants'

function NewFilterSet({ title, fields, choices, handleFilterChange, filterValues }) {
    console.log("Fields", fields)
    const components = fields.map((field, index) => {
      if(field.type === 'choice' ) {
        return <ChoiceInput
          handleFilterChange={handleFilterChange}
          filterValues={filterValues}
          label={ field.title }
          filter={ field.name }
          choices={choices[field.name.toUpperCase()]}
          key={index}
        />
      } else if (field.type === 'date') {
        return <DateRangeInput
          handleFilterChange={handleFilterChange}
          filterValues={filterValues}
          label={`${field.title} between`}
          filter={ field.name }
          key={index}
        />
      } else if (field.type === 'text') {
        return <TextInput
          handleFilterChange={handleFilterChange}
          filterValues={filterValues}
          label={ field.title }
          filter={ field.name }
          key={index}
        />
      } else if (field.type === 'radio') {
        return <RadioPillInput
          handleFilterChange={handleFilterChange}
          filterValues={filterValues}
          label={ field.title }
          filter={ field.name }
          key={index}
        />
      } else if (field.type === 'bool') {
        return <BoolInput
          handleFilterChange={handleFilterChange}
          filterValues={filterValues}
          label={`${field.title}?`}
          filter={field.name}
          key={index}
        />
      } else if (field.type === 'autocomplete'){
        console.log("IN AUTOCOMPLETE")
        if(AUTOCOMPLETE_MULTI_FILTERS.includes(field.name)) {
          console.log("MULTI")
          return <AutocompleteInput
            handleFilterChange={handleFilterChange}
            filterValues={filterValues}
            label={ field.title }
            filter={field.name}
            type={field.autocomplete_type}
            isSingle={false}
            key={index}
          />
        } else if(AUTOCOMPLETE_SINGLE_FILTERS.includes(field.name)) {
          console.log("SINGLE")
          return <AutocompleteInput
            handleFilterChange={handleFilterChange}
            filterValues={filterValues}
            label={field.title}
            filter={field.name}
            type={field.autocomplete_type}
            isSingle={true}
            key={index}
          />
        } else {
          console.error('This field has not been assigned to single or multi autocomplete.')
          return null
        }
      } else {
        console.error('Unknown field type.')
        return null
      }

    })
    return (
      <div className="filters__set">
        {components}
      </div>
    )
}


export default NewFilterSet
