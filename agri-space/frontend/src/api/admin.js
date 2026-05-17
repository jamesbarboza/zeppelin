import client from './client'

export const listUsers = () => client.get('/admin/users/').then(r => r.data)
export const updateUser = (id, data) => client.patch(`/admin/users/${id}/`, data).then(r => r.data)
export const getAnalytics = () => client.get('/admin/analytics/').then(r => r.data)
