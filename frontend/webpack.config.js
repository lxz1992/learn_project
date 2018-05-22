const path = require('path');
const webpack = require('webpack');
const extractTextPlugin = require('extract-text-webpack-plugin');
const cleanWebpackPlugin = require('clean-webpack-plugin');
const htmlWebpackPlugin = require('html-webpack-plugin');
const webpackGitHash = require('webpack-git-hash');
const copyWebpackPlugin = require('copy-webpack-plugin');
let childProcess = require('child_process');
const htmlStringReplace = require('html-string-replace-webpack-plugin');

const gitHashLength = 7;
const gitHash = childProcess
  .execSync('git rev-parse HEAD')
  .toString()
  .substring(0, gitHashLength);

// the path(s) that should be cleaned
let pathsToClean = ['dist']

// the clean options to use
let cleanOptions = {
  verbose: true,
  dry: false
};

module.exports = {
  entry: {
    vendor: [
      'jquery', 'bootstrap', 'jquery-ui', 'highcharts', 'datatables.net'
    ],
    vend_mvc: [
      "redux",
      "redux-actions",
      "redux-logger",
      "redux-persist",
      "redux-promise",
      "redux-promise-middleware",
      "redux-route",
      "redux-thunk",
      "redux-watch"
    ],
    main: [
      'babel-polyfill', './main_sys/src/index.js'
    ],
    md_analysis: [
      'babel-polyfill', './main_sys/src/index.js', './md_analysis/src/index.js'
    ],
    cr_review: [
      'babel-polyfill', './main_sys/src/index.js', './cr_review_sys/src/index.js'
    ],
    oauth_redirect: ['babel-polyfill', './main_sys/src/oauth_token.js']
  },
  output: {
    filename: '[name].[id].[githash].js',
    path: path.resolve(__dirname, 'dist')
  },
  module: {
    rules: [
      {
        test: /.jsx?$/,
        include: [
          path.resolve(__dirname, 'cr_review_sys', 'src'),
          path.resolve(__dirname, 'md_analysis', 'src'),
          path.resolve(__dirname, 'main_sys', 'src')
        ],
        exclude: /(node_modules|bower_components)/,
        loader: 'babel-loader',
        options: {
          presets: ['env'],
          plugins: [require('babel-plugin-transform-object-rest-spread')]
        }
      }, {
        test: /\.s?css$/,
        use: extractTextPlugin.extract({
          use: [
            {
              loader: "css-loader"
            }, {
              loader: "sass-loader",
              options: {
                includePath: ['./cr_review_sys/resources/css']
              }
            }
          ],
          fallback: "style-loader"
        })
      },
      // {   test: /\.s?css$/,   use: [     {       loader: "style-loader" // creates
      // style nodes from JS strings     }, {       loader: "css-loader" // translates
      // CSS into CommonJS     }, {       loader: "sass-loader" // compiles Sass to
      // CSS     }   ] },
      {
        test: /\.(jpg|png)$/,
        loader: 'file-loader'
      }, {
        test: /\.woff(2)?(\?v=[0-9]\.[0-9]\.[0-9])?$/,
        loader: "url-loader?limit=10000&mimetype=application/font-woff"
      }, {
        test: /\.(ttf|eot|svg)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
        loader: "file-loader"
      }, {
        test: /\.html$/,
        use: [
          {
            loader: 'html-loader',
            options: {
              minimize: false
            }
          }
        ]
      }
    ]
  },
  resolve: {
    extensions: ['.json', '.js', '.jsx']
  },
  devtool: 'source-map',
  devServer: {
    historyApiFallback: true,
    headers: {
      'Access-Control-Allow-Origin': '*'
    }
  },
  plugins: [
    new cleanWebpackPlugin(pathsToClean, cleanOptions),
    new webpack.NoEmitOnErrorsPlugin(),
    new webpack.ProvidePlugin({$: 'jquery', jQuery: 'jquery', 'window.jQuery': 'jquery', 'window.$': 'jquery', 'Highcharts': 'highcharts'}),
    new webpack
      .optimize
      .CommonsChunkPlugin({
        names: [
          "vendor", "vend_mvc"
        ],
        minChunks: Infinity,
        children: false
      }),
    new extractTextPlugin({
      allChunks: true,
      filename: (getPath) => {
        return getPath('[name].[id].[contenthash:' + gitHashLength + '].css').replace(/\.(\w{7})\.css/, '.' + gitHash + '.css');
      }
    }),
    new htmlWebpackPlugin({
      filename: 'md_analysis.html',
      template: './md_analysis/templates/index_gen.html',
      chunks: ['vend_mvc', 'vendor', 'md_analysis']
    }),
    new htmlWebpackPlugin({
      filename: 'cr_review.html',
      template: './cr_review_sys/templates/index_gen.html',
      chunks: ['vend_mvc', 'vendor', 'cr_review']
    }),
    new htmlWebpackPlugin({
      filename: 'home.html',
      template: './main_sys/templates/home_gen.html',
      chunks: ['vend_mvc', 'vendor', 'main']
    }),
    new htmlWebpackPlugin({
      filename: 'home.html',
      template: './main_sys/templates/home_gen.html',
      chunks: ['vend_mvc', 'vendor', 'main']
    }),
    new htmlWebpackPlugin({
      filename: 'login.html',
      template: './main_sys/templates/login_gen.html',
      chunks: ['vend_mvc', 'vendor', 'main']
    }),
    new htmlWebpackPlugin({
      filename: 'oauth_redirect.html',
      template: './main_sys/templates/oauth_redirect.html',
      chunks: ['vend_mvc', 'vendor', 'oauth_redirect']
    }),
    new htmlStringReplace({
      enable: true,
      patterns: [
        {
          match: /\@frontend\-version\@/g,
          replacement: `${require("./package.json").version}`
        }
      ]
    }),
    new webpackGitHash({hashLength: gitHashLength}),
    new webpack.DefinePlugin({
      'process.env': {
        'NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'development')
      }
    })
  ]
};