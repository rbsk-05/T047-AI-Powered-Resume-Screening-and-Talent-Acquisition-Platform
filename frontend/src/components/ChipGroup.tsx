export function ChipGroup({ label, items, tone = "neutral" }: { label: string; items: string[]; tone?: "neutral" | "preferred" }) {
  return (
    <div className="profile-group">
      <h3>{label}</h3>
      {items.length ? (
        <div className="chips">
          {items.map((item) => (
            <span className={`chip ${tone}`} key={item}>
              {item}
            </span>
          ))}
        </div>
      ) : (
        <p className="empty">None detected</p>
      )}
    </div>
  );
}
