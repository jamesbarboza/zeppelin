import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import PlotMap from '../components/PlotMap'
import { createPlot, listCropTags } from '../api/plots'

export default function NewPlot() {
  const [geometry, setGeometry] = useState(null)
  const [name, setName] = useState('')
  const [cropTags, setCropTags] = useState([])
  const [selectedTags, setSelectedTags] = useState([])
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    listCropTags().then(setCropTags)
  }, [])

  const toggleTag = (id) => {
    setSelectedTags(prev => prev.includes(id) ? prev.filter(t => t !== id) : [...prev, id])
  }

  const handleSave = async () => {
    if (!name.trim()) return setError('Plot name is required.')
    if (!geometry) return setError('Click the map to set a location, or draw a boundary.')
    setSaving(true)
    try {
      const plot = await createPlot({ name: name.trim(), geometry, crop_tag_ids: selectedTags })
      navigate(`/plots/${plot.id}`)
    } catch {
      setError('Failed to save plot. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <PlotMap onGeometryChange={setGeometry} height="50vh" />
      <div style={{ padding: '1.5rem', maxWidth: 640, margin: '0 auto' }}>
        <h2 style={{ marginBottom: '1rem' }}>New Plot</h2>
        <label style={{ display: 'block', marginBottom: 6, fontWeight: 600 }}>Plot Name</label>
        <input value={name} onChange={e => setName(e.target.value)} placeholder="e.g. North Field"
          style={{ width: '100%', padding: '8px 12px', marginBottom: 16, border: '1px solid #ddd', borderRadius: 4 }} />
        <label style={{ display: 'block', marginBottom: 8, fontWeight: 600 }}>Crops (optional)</label>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 16 }}>
          {cropTags.map(tag => (
            <button key={tag.id} onClick={() => toggleTag(tag.id)}
              style={{ padding: '4px 12px', borderRadius: 20, cursor: 'pointer',
                       background: selectedTags.includes(tag.id) ? '#1a3a2a' : 'white',
                       color: selectedTags.includes(tag.id) ? 'white' : '#1a3a2a',
                       border: '1px solid #1a3a2a' }}>
              {tag.name}
            </button>
          ))}
        </div>
        {geometry && (
          <p style={{ color: '#2e7d32', marginBottom: 12, fontSize: 14 }}>
            ✓ Location set ({geometry.type === 'Point' ? 'pin' : 'polygon boundary'})
          </p>
        )}
        {error && <p style={{ color: '#c0392b', marginBottom: 12, fontSize: 14 }}>{error}</p>}
        <button onClick={handleSave} disabled={saving}
          style={{ padding: '10px 24px', background: '#1a3a2a', color: 'white',
                   border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 'bold' }}>
          {saving ? 'Saving...' : 'Save Plot'}
        </button>
      </div>
    </div>
  )
}
