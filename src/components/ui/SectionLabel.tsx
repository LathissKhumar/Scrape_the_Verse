export function SectionLabel({
  stage,
  label,
}: {
  stage?: string
  label: string
}) {
  return (
    <div className="flex items-center justify-center gap-3 mb-4">
      {stage && (
        <span
          className="text-xs font-mono tracking-widest border px-2 py-0.5 rounded"
          style={{ color: '#EC0AFF', borderColor: 'rgba(236,10,255,0.4)' }}
        >
          STAGE {stage}
        </span>
      )}
      <span
        className="text-xs font-mono tracking-widest uppercase"
        style={{ color: '#A1A1B5' }}
      >
        {label}
      </span>
    </div>
  )
}
