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
          className="text-xs font-mono font-bold tracking-widest border px-2.5 py-0.5 rounded-md shadow-sm"
          style={{ color: '#38BDF8', borderColor: 'rgba(56, 189, 248, 0.5)', backgroundColor: 'rgba(56, 189, 248, 0.1)' }}
        >
          STAGE {stage}
        </span>
      )}
      <span
        className="text-xs font-mono font-semibold tracking-widest uppercase"
        style={{ color: '#CBD5E1' }}
      >
        {label}
      </span>
    </div>
  )
}
