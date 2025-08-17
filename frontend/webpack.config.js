// Webpack configuration to disable caching during development
module.exports = (config, env) => {
  if (env === 'development') {
    // Disable caching
    config.cache = false;
    
    // Add cache control headers
    config.devServer = {
      ...config.devServer,
      headers: {
        'Cache-Control': 'no-store, no-cache, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    };
  }
  
  return config;
};