import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import PlotMap from '../components/PlotMap'
import RecommendationList from '../components/RecommendationList'
import { getPlot, deletePlot } from '../api/plots'

export default function PlotDetail() {
  const { id } = useParams()
  const [plot, setPlot] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    getPlot(id).then(setPlot)
  }, [id])

  const handleDelete = async () => {
    if (!confirm(`Delete "${plot.name}"?`)) return
    await deletePlot(id)
    navigate('/dashboard')
  }

  if (!plot) return <div className="loading">Loading plot...</div>

  return (
    <div>
      <PlotMap existingGeometry={plot.geometry} height="40vh" />
      <div style={{ padding: '1.5rem', maxWidth: 640, margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
          <div>
            <h2>{plot.name}</h2>
            <p style={{ color: '#666', fontSize: 14, marginTop: 4 }}>
              {plot.crop_tags.map(t => t.name).join(', ') || 'No crops tagged'}
              {plot.area_hectares ? ` · ${plot.area_hectares.toFixed(1)} ha` : ''}
            </p>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <Link to={`/plots/${id}/edit`}
              style={{ padding: '6px 16px', border: '1px solid #1a3a2a', color: '#1a3a2a',
                       borderRadius: 4, textDecoration: 'none', fontSize: 14 }}>
              Edit
            </Link>
            <button onClick={handleDelete}
              style={{ padding: '6px 16px', background: '#c0392b', color: 'white',
                       border: 'none', borderRadius: 4, cursor: 'pointer', fontSize: 14 }}>
              Delete
            </button>
          </div>
        </div>
        <RecommendationList plotId={id} />
      </div>
    </div>
  )
}
