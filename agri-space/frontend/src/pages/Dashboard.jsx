import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import PlotMap from '../components/PlotMap'
import RecommendationList from '../components/RecommendationList'
import { listPlots } from '../api/plots'

export default function Dashboard() {
  const [plots, setPlots] = useState([])
  const [selectedPlotId, setSelectedPlotId] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    listPlots().then(data => {
      setPlots(data)
      if (data.length > 0) setSelectedPlotId(data[0].id)
    })
  }, [])

  const selectedPlot = plots.find(p => p.id === selectedPlotId)

  return (
    <div>
      <PlotMap existingGeometry={selectedPlot?.geometry ?? null} height="45vh" />
      <div style={{ padding: '1.5rem', maxWidth: 800, margin: '0 auto' }}>
        {plots.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem 0', color: '#666' }}>
            <p style={{ fontSize: 18, marginBottom: 12 }}>No plots yet.</p>
            <button onClick={() => navigate('/plots/new')}
              style={{ padding: '10px 24px', background: '#1a3a2a', color: 'white',
                       border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 'bold' }}>
              + Add Your First Plot
            </button>
          </div>
        ) : (
          <>
            <div style={{ display: 'flex', gap: 8, marginBottom: '1.5rem', flexWrap: 'wrap' }}>
              {plots.map(p => (
                <button key={p.id} onClick={() => setSelectedPlotId(p.id)}
                  style={{ padding: '6px 16px', borderRadius: 20, cursor: 'pointer',
                           background: selectedPlotId === p.id ? '#1a3a2a' : 'white',
                           color: selectedPlotId === p.id ? 'white' : '#1a3a2a',
                           border: '1px solid #1a3a2a',
                           fontWeight: selectedPlotId === p.id ? 'bold' : 'normal' }}>
                  {p.name}
                </button>
              ))}
              <button onClick={() => navigate('/plots/new')}
                style={{ padding: '6px 16px', borderRadius: 20, cursor: 'pointer',
                         background: 'transparent', color: '#666', border: '1px dashed #ccc' }}>
                + Add Plot
              </button>
            </div>
            {selectedPlotId && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <div>
                    <h2 style={{ fontSize: 18 }}>{selectedPlot?.name}</h2>
                    <p style={{ fontSize: 13, color: '#888' }}>
                      {selectedPlot?.crop_tags?.map(t => t.name).join(', ') || 'No crops tagged'}
                    </p>
                  </div>
                  <button onClick={() => navigate(`/plots/${selectedPlotId}`)}
                    style={{ padding: '6px 14px', border: '1px solid #1a3a2a', color: '#1a3a2a',
                             background: 'transparent', borderRadius: 4, cursor: 'pointer', fontSize: 13 }}>
                    View Full Detail →
                  </button>
                </div>
                <RecommendationList plotId={selectedPlotId} />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
