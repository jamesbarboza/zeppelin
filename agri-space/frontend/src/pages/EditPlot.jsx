import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import PlotMap from '../components/PlotMap'
import { getPlot, updatePlot, listCropTags } from '../api/plots'

export default function EditPlot() {
  const { id } = useParams()
  const [plot, setPlot] = useState(null)
  const [geometry, setGeometry] = useState(null)
  const [name, setName] = useState('')
  const [cropTags, setCropTags] = useState([])
  const [selectedTags, setSelectedTags] = useState([])
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    Promise.all([getPlot(id), listCropTags()]).then(([p, tags]) => {
      setPlot(p)
      setName(p.name)
      setGeometry(p.geometry)
      setSelectedTags(p.crop_tags.map(t => t.id))
      setCropTags(tags)
    })
  }, [id])

  const toggleTag = (tagId) => {
    setSelectedTags(prev => prev.includes(tagId) ? prev.filter(t => t !== tagId) : [...prev, tagId])
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      await updatePlot(id, { name: name.trim(), geometry, crop_tag_ids: selectedTags })
      navigate(`/plots/${id}`)
    } catch {
      setError('Failed to save changes.')
    } finally {
      setSaving(false)
    }
  }

  if (!plot) return <div className="loading">Loading...</div>

  return (
    <div>
      <PlotMap onGeometryChange={setGeometry} existingGeometry={plot.geometry} height="45vh" />
      <div style={{ padding: '1.5rem', maxWidth: 640, margin: '0 auto' }}>
        <h2 style={{ marginBottom: '1rem' }}>Edit Plot</h2>
        <label style={{ display: 'block', marginBottom: 6, fontWeight: 600 }}>Plot Name</label>
        <input value={name} onChange={e => setName(e.target.value)}
          style={{ width: '100%', padding: '8px 12px', marginBottom: 16, border: '1px solid #ddd', borderRadius: 4 }} />
        <label style={{ display: 'block', marginBottom: 8, fontWeight: 600 }}>Crops</label>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 20 }}>
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
        {error && <p style={{ color: '#c0392b', marginBottom: 12 }}>{error}</p>}
        <div style={{ display: 'flex', gap: 12 }}>
          <button onClick={handleSave} disabled={saving}
            style={{ padding: '10px 24px', background: '#1a3a2a', color: 'white',
                     border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 'bold' }}>
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
          <button onClick={() => navigate(`/plots/${id}`)}
            style={{ padding: '10px 24px', background: 'white', color: '#666',
                     border: '1px solid #ccc', borderRadius: 4, cursor: 'pointer' }}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}
