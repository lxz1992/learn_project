const path = require('path');
const webpack = require('webpack');
const common = require('./webpack.config.js');
const uglifyJsPlugin = require('uglifyjs-webpack-plugin');

common
  .plugins
  .push(new uglifyJsPlugin({
    parallel: 4,
    cache: false,
    sourceMap: true,
    uglifyOptions: {
      mangle: true,
      compress: {
        warnings: true
      },
      warnings: true
    }
  }));

module.exports = {
  ...common,
  output: {
    filename: '[name].[id].[githash].js',
    path: path.resolve(__dirname, 'dist'),
    publicPath: '/static/'
  }
};
