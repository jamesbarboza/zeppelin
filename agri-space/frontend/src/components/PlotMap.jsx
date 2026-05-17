import { useEffect, useRef, useState } from 'react'
import L from 'leaflet'
import 'leaflet-draw/dist/leaflet.draw.css'
import 'leaflet-draw'

export default function PlotMap({ onGeometryChange, existingGeometry = null, height = '50vh' }) {
  const mapRef = useRef(null)
  const mapInstanceRef = useRef(null)
  const drawnLayersRef = useRef(null)
  const [mode, setMode] = useState('pin')

  useEffect(() => {
    if (mapInstanceRef.current) return

    const map = L.map(mapRef.current).setView([-28.5, 24.5], 6)
    mapInstanceRef.current = map

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(map)

    const drawnItems = new L.FeatureGroup()
    map.addLayer(drawnItems)
    drawnLayersRef.current = drawnItems

    if (existingGeometry) {
      const layer = L.geoJSON(existingGeometry)
      drawnItems.addLayer(layer)
      map.fitBounds(layer.getBounds())
    }

    map.on('click', (e) => {
      if (mode !== 'pin') return
      drawnItems.clearLayers()
      const marker = L.marker(e.latlng)
      drawnItems.addLayer(marker)
      onGeometryChange?.({
        type: 'Point',
        coordinates: [e.latlng.lng, e.latlng.lat]
      })
    })

    map.on(L.Draw.Event.CREATED, (e) => {
      drawnItems.clearLayers()
      drawnItems.addLayer(e.layer)
      onGeometryChange?.(e.layer.toGeoJSON().geometry)
    })

    return () => { map.remove(); mapInstanceRef.current = null }
  }, [])

  const activatePolygonDraw = () => {
    setMode('polygon')
    drawnLayersRef.current?.clearLayers()
    const drawControl = new L.Draw.Polygon(mapInstanceRef.current)
    drawControl.enable()
  }

  const switchToPin = () => {
    setMode('pin')
    drawnLayersRef.current?.clearLayers()
    onGeometryChange?.(null)
  }

  return (
    <div style={{ position: 'relative' }}>
      <div ref={mapRef} style={{ height, width: '100%' }} />
      <div style={{ position: 'absolute', top: 12, right: 12, zIndex: 1000, display: 'flex', gap: 8 }}>
        <button onClick={switchToPin}
          style={{ padding: '6px 14px', background: mode === 'pin' ? '#1a3a2a' : 'white',
                   color: mode === 'pin' ? 'white' : '#1a3a2a', border: '1px solid #1a3a2a',
                   borderRadius: 4, cursor: 'pointer', fontWeight: 'bold' }}>
          📍 Pin
        </button>
        <button onClick={activatePolygonDraw}
          style={{ padding: '6px 14px', background: mode === 'polygon' ? '#1a3a2a' : 'white',
                   color: mode === 'polygon' ? 'white' : '#1a3a2a', border: '1px solid #1a3a2a',
                   borderRadius: 4, cursor: 'pointer', fontWeight: 'bold' }}>
          ⬡ Draw Boundary
        </button>
      </div>
    </div>
  )
}
