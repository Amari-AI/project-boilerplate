const config = {
  API_URL: process.env.REACT_APP_API_URL || (
    process.env.NODE_ENV === 'production' 
      ? '/api'  // In production, nginx will proxy /api to backend
      : 'http://localhost:8000'
  )
};

export default config;