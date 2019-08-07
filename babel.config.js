// babel.config.js
module.exports = api => {
  const isTest = api.env('test')
  if (isTest) {
    return {
      presets: [
        [
          '@babel/preset-env',
          {
            modules: false,
          },
        ],
        '@babel/preset-react',
      ],
      plugins: [
        "transform-es2015-modules-commonjs",
      ],
    }
  } else {
    return {
      presets: [
        [
          '@babel/preset-env',
          {
            modules: false,
          },
        ],
        '@babel/preset-react',
      ],
    }
  }
};