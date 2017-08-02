# Filters

There is no single definition file for filters in this app.
Various front-end changes need to be made when filters are added, removed, or changed.

- New filter fields should be added to the appropriate constants in `constants.js`.
    - `ALL_FILTERS` for any field.
    - `DATE_FILTERS`, `AUTOCOMPLETE_SINGLE_FILTERS`, or `AUTOCOMPLETE_MULTI_FILTERS` for any filter of those types.
- Input components in `FilterSets.js` should be amended.
- The associated `FilterSets[category_name].fields` list should be updated.
  For instance, if I change the `General` field `state` to `state_or_province`, `FilterSets['General'].fields` needs to be updated.
- The `FilterSets` object should have an aliased key if a category name changes.
  You can see an example with this for `Arrest / Detention` in `FilterSets.js`.
  This is likely the culprit if you change the name of a category and the associated filters no longer change.
