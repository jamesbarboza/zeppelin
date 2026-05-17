import client from './client'

export const getRecommendations = (plotId) =>
  client.get(`/plots/${plotId}/recommendations/`).then(r => r.data)
