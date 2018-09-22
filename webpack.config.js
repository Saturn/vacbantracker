const path = require('path');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
// const UglifyJsPlugin = require("uglifyjs-webpack-plugin");
// const OptimizeCSSAssetsPlugin = require("optimize-css-assets-webpack-plugin");


module.exports = {
  entry: ['./app/resources/js/app.js', './app/resources/scss/main.scss'],
  output: {
    path: path.resolve(__dirname, 'app/static/'),
    filename: 'js/app.js'
  },
  module: {
    rules: [
      {
        test: /\.scss$/,
        use: [
          MiniCssExtractPlugin.loader,
          { loader: 'css-loader', options: { minimize: true } },
          'sass-loader'
        ]
      }
    ]
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: 'css/app.css'
    })
  ]
};
