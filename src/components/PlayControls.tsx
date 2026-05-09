interface Props {
  isPlaying: boolean
  step: number
  total: number
  currentLabel: string
  speed: number
  onPlay: () => void
  onPause: () => void
  onNext: () => void
  onReset: () => void
  onSpeedChange: (ms: number) => void
}

export default function PlayControls({
  isPlaying, step, total, currentLabel, speed,
  onPlay, onPause, onNext, onReset, onSpeedChange,
}: Props) {
  const iconBtn = (onClick: () => void, icon: string, disabled = false) => (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{
        width: 30,
        height: 30,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: 13,
        background: 'none',
        border: 'none',
        borderRadius: 6,
        cursor: disabled ? 'not-allowed' : 'pointer',
        color: disabled ? '#d1d5db' : '#111827',
        transition: 'background 0.1s',
      }}
    >
      {icon}
    </button>
  )

  const progress = total > 1 ? (step / (total - 1)) * 100 : 0

  return (
    <div style={{
      position: 'absolute',
      bottom: 24,
      left: '50%',
      transform: 'translateX(-50%)',
      background: '#ffffff',
      border: '1px solid #e5e7eb',
      borderRadius: 40,
      padding: '6px 14px 6px 10px',
      display: 'flex',
      alignItems: 'center',
      gap: 2,
      boxShadow: '0 4px 20px rgba(0,0,0,0.07), 0 1px 4px rgba(0,0,0,0.04)',
      userSelect: 'none',
      whiteSpace: 'nowrap',
      fontFamily: 'Inter, system-ui, sans-serif',
    }}>
      {iconBtn(onReset, '⏮', step === 0 && !isPlaying)}
      {isPlaying
        ? iconBtn(onPause, '⏸')
        : iconBtn(onPlay, '▶', step >= total - 1)}
      {iconBtn(onNext, '⏭', isPlaying || step >= total - 1)}

      <div style={{ width: 1, height: 16, background: '#e5e7eb', margin: '0 10px' }} />

      <div style={{ display: 'flex', flexDirection: 'column', gap: 3, minWidth: 140, maxWidth: 200 }}>
        <span style={{
          fontSize: 11,
          fontWeight: 500,
          color: '#111827',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          lineHeight: 1.2,
        }}>
          {currentLabel}
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
          <div style={{ flex: 1, height: 2, background: '#f0f0f0', borderRadius: 1, overflow: 'hidden' }}>
            <div style={{
              height: '100%',
              width: `${progress}%`,
              background: '#111827',
              borderRadius: 1,
              transition: 'width 0.25s ease',
            }} />
          </div>
          <span style={{
            fontSize: 10,
            color: '#9ca3af',
            flexShrink: 0,
            fontVariantNumeric: 'tabular-nums',
          }}>
            {step + 1}/{total}
          </span>
        </div>
      </div>

      <div style={{ width: 1, height: 16, background: '#e5e7eb', margin: '0 10px' }} />

      <select
        value={speed}
        onChange={(e) => onSpeedChange(Number(e.target.value))}
        style={{
          fontSize: 11,
          border: 'none',
          background: 'none',
          color: '#6b7280',
          cursor: 'pointer',
          outline: 'none',
          padding: 0,
          fontFamily: 'inherit',
        }}
      >
        <option value={2000}>0.5×</option>
        <option value={1000}>1×</option>
        <option value={500}>2×</option>
        <option value={250}>4×</option>
      </select>
    </div>
  )
}
