const STATUS_CONFIG = {
  green: { bg: '#e8f5e9', border: '#43a047', icon: '🟢' },
  amber: { bg: '#fff8e1', border: '#f9a825', icon: '🟡' },
  red:   { bg: '#ffebee', border: '#e53935', icon: '🔴' },
}

const ACTIVITY_LABELS = {
  spray: '🌿 Spray', irrigate: '💧 Irrigate', plant: '🌱 Plant', harvest: '🌾 Harvest'
}

export default function RecommendationCard({ card }) {
  const cfg = STATUS_CONFIG[card.status] ?? STATUS_CONFIG.amber

  return (
    <div style={{ background: cfg.bg, border: `1px solid ${cfg.border}`, borderLeft: `4px solid ${cfg.border}`,
                  borderRadius: 8, padding: '1rem 1.25rem', marginBottom: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div style={{ fontSize: 12, fontWeight: 600, color: '#666', textTransform: 'uppercase', marginBottom: 4 }}>
            {ACTIVITY_LABELS[card.activity] ?? card.activity}
          </div>
          <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 4 }}>{card.title}</div>
          <div style={{ fontSize: 13, color: '#555' }}>{card.reason}</div>
        </div>
        <span style={{ fontSize: 22, marginLeft: 12 }}>{cfg.icon}</span>
      </div>
    </div>
  )
}
