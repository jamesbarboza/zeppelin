import RecommendationCard from './RecommendationCard'
import useRecommendations from '../hooks/useRecommendations'

export default function RecommendationList({ plotId }) {
  const { cards, loading, error } = useRecommendations(plotId)

  if (loading) return (
    <div style={{ padding: '2rem', textAlign: 'center', color: '#888' }}>
      Analyzing weather conditions...
    </div>
  )
  if (error) return <p style={{ color: '#c0392b', padding: '1rem' }}>{error}</p>

  const sorted = [...cards].sort((a, b) => {
    const order = { red: 0, amber: 1, green: 2 }
    return (order[a.status] ?? 3) - (order[b.status] ?? 3)
  })

  return (
    <div>
      <h3 style={{ marginBottom: '1rem', fontSize: 14, fontWeight: 600,
                   textTransform: 'uppercase', color: '#666', letterSpacing: '0.05em' }}>
        Today's Recommendations
      </h3>
      {sorted.map((card, i) => <RecommendationCard key={i} card={card} />)}
    </div>
  )
}
