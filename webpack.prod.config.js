const path = require('path');
const glob = require('glob');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const UglifyJsPlugin = require("uglifyjs-webpack-plugin");
const OptimizeCSSAssetsPlugin = require("optimize-css-assets-webpack-plugin");
const PurifyCSSPlugin = require('purifycss-webpack');
const CopyWebpackPlugin = require('copy-webpack-plugin');


module.exports = {
  mode: 'production',
  entry: './app/frontend/js/app.js',
  output: {
    path: path.resolve(__dirname, 'app/static/'),
    filename: 'js/app.js'
  },
  optimization: {
    minimizer: [
      new UglifyJsPlugin({
        cache: true,
        parallel: true
      }),
      new OptimizeCSSAssetsPlugin({})
    ]
  },
  module: {
    rules: [
      {
        test: /\.scss$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          'sass-loader'
        ]
      },
      {
        test: /\.js$/,
        exclude: /(node_modules)/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env']
          }
        }
      }
    ]
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: 'css/app.css',
      chunkFilename: '[id].css'
    }),
    new CopyWebpackPlugin([
      {
        from: './app/frontend/*',
        flatten: true
      },
    ]),
    new PurifyCSSPlugin({
      paths: glob.sync('{' + path.join(__dirname, 'app/templates/**/*.j2') + ',' +
                       path.join(__dirname, 'app/frontend/js/*.js') + '}'
                      ),
      purifyOptions: {
        whitelist: ['d-none']
      }
    })
  ]
};
