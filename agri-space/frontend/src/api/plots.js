import client from './client'

export const listPlots = () => client.get('/plots/').then(r => r.data)
export const getPlot = (id) => client.get(`/plots/${id}/`).then(r => r.data)
export const createPlot = (data) => client.post('/plots/', data).then(r => r.data)
export const updatePlot = (id, data) => client.patch(`/plots/${id}/`, data).then(r => r.data)
export const deletePlot = (id) => client.delete(`/plots/${id}/`)
export const listCropTags = () => client.get('/crop-tags/').then(r => r.data)
