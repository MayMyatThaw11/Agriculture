// Deployments may override the API location
// this with VITE_API_BASE_URL (for example, https://api.example.com/api).
export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '')
export const API_ENABLED = import.meta.env.VITE_ENABLE_API === 'true'
