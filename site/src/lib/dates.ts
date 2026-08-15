/** Shared date formatting so every page renders periods identically. */

const MONTHS = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

export interface Period {
  start: string;
  end: string | null;
}

/** "2024-11" -> "Nov 2024" */
export function month(ym: string): string {
  const [year, mon] = ym.split("-");
  return `${MONTHS[Number(mon) - 1]} ${year}`;
}

/**
 * Render a period the way a reader expects:
 *   2024-11 .. null      -> "2024 — present"
 *   2023-08 .. 2024-04   -> "2023 — 2024"
 *   2024-04 .. 2024-10   -> "Apr — Oct 2024"   (not the useless "2024 — 2024")
 */
export function period(p: Period): string {
  const startYear = p.start.slice(0, 4);
  if (!p.end) return `${startYear} — present`;

  const endYear = p.end.slice(0, 4);
  if (startYear === endYear) {
    const startMonth = MONTHS[Number(p.start.slice(5, 7)) - 1];
    const endMonth = MONTHS[Number(p.end.slice(5, 7)) - 1];
    return startMonth === endMonth
      ? `${startMonth} ${startYear}`
      : `${startMonth} — ${endMonth} ${startYear}`;
  }
  return `${startYear} — ${endYear}`;
}

/** Full precision, for case-study fact lists: "Nov 2024 — present" */
export function periodLong(p: Period): string {
  return `${month(p.start)} — ${p.end ? month(p.end) : "present"}`;
}
