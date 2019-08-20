// jest.config.js
module.exports = {
  verbose: true,
  moduleNameMapper: {
    '^~/(.*)$': '<rootDir>/client/common/js/$1',
    '^WagtailAutocomplete/(.*)$': '<rootDir>/client/autocomplete/js/components/$1',
  },
  setupFiles: ["<rootDir>/client/common/js/setupTests.js"],
}
