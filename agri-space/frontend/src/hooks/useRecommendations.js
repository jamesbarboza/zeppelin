import { useState, useEffect } from 'react'
import { getRecommendations } from '../api/recommendations'

export default function useRecommendations(plotId) {
  const [cards, setCards] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!plotId) return
    setLoading(true)
    getRecommendations(plotId)
      .then(data => { setCards(data); setLoading(false) })
      .catch(() => { setError('Could not load recommendations.'); setLoading(false) })
  }, [plotId])

  return { cards, loading, error }
}
