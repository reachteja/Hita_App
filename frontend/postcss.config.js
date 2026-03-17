/*module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};*/

export default {
  plugins: {
    '@tailwindcss/postcss': {}, // The new package name
    // autoprefixer: {},      <-- You can likely remove this now!
  },
}

