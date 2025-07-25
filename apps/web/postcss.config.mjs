const config = {
  plugins: {
    'postcss-import': {},
    'tailwindcss': {},
    'postcss-nesting': {},
    autoprefixer: {},
    ...(process.env.NODE_ENV === 'production' ? { cssnano: {} } : {})
  },
};

export default config;
