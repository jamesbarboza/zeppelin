import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  withCredentials: true,
})

client.interceptors.response.use(
  (res) => res,
  async (err) => {
    const isRefresh = err.config?.url?.includes('/auth/refresh/')
    if (err.response?.status === 401 && !err.config._retry && !isRefresh) {
      err.config._retry = true
      try {
        await axios.post('/api/auth/refresh/', {}, { withCredentials: true })
        return client(err.config)
      } catch {
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(err)
  }
)

export default client
