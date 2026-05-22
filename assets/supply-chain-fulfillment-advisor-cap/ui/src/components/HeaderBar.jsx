import { COLORS } from '../tokens';

const ACCENT_BLUE = '#4fc3f7';

export default function HeaderBar({ onAnalyze, salesOrderId, onSalesOrderChange, loading }) {
  return (
    <header style={{
      background: COLORS.bgCard,
      borderBottom: `1px solid ${COLORS.border}`,
      padding: '0 24px',
      height: 56,
      display: 'flex',
      alignItems: 'center',
      gap: 16,
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, flex: '0 0 auto' }}>
        <div style={{
          width: 32, height: 32, borderRadius: 8,
          background: 'linear-gradient(135deg, #4fc3f7 0%, #2ec4b6 100%)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 16,
        }}>&#9889;</div>
        <span style={{ color: COLORS.textPrimary, fontWeight: 700, fontSize: 15, letterSpacing: '0.02em' }}>
          Supply Chain Fulfillment Advisor
        </span>
      </div>
      <div style={{ flex: 1 }} />
      <input
        value={salesOrderId}
        onChange={e => onSalesOrderChange(e.target.value)}
        placeholder="Sales Order ID"
        style={{
          background: COLORS.bgNavy,
          border: `1px solid ${COLORS.border}`,
          borderRadius: 6,
          color: COLORS.textPrimary,
          padding: '6px 12px',
          fontSize: 13,
          width: 160,
          outline: 'none',
        }}
      />
      <button
        onClick={onAnalyze}
        disabled={loading}
        style={{
          background: loading ? COLORS.border : ACCENT_BLUE,
          color: loading ? COLORS.textMuted : '#0d1b2a',
          border: 'none',
          borderRadius: 6,
          padding: '7px 18px',
          fontWeight: 600,
          fontSize: 13,
          cursor: loading ? 'not-allowed' : 'pointer',
          transition: 'background 0.2s',
          whiteSpace: 'nowrap',
        }}
      >
        {loading ? 'Analyzing...' : 'Run Analysis'}
      </button>
    </header>
  );
}
