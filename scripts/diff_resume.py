"""
Side-by-side diff between two rendered resumes, compared as the reader sees them.

    python scripts/diff_resume.py acme                # vs the PDF the site ships
    python scripts/diff_resume.py acme --against base # vs another variant
    python scripts/diff_resume.py acme --live         # vs the PDF live on the site
    python scripts/diff_resume.py acme --git          # also print a git diff in the terminal
    python scripts/diff_resume.py acme --git --word   # ...word-level
    python scripts/diff_resume.py acme --no-open      # don't open the browser

It diffs the text extracted back out of the *rendered PDFs*, not the variant JSON. The
JSON says which ids were picked; only the PDF says what a recruiter actually reads, and
the deployed copy has no variant file behind it to compare against anyway.

Extracted text wraps at the page edge, which would turn one reworded bullet into a
noisy multi-line hunk. So wrapped lines are rejoined first: one bullet, one line.

Both sides are rendered fresh (except the deployed copy, which is read as-is), the text
is written next to each PDF as resume.txt, and the diff is saved twice: a side-by-side
page, resume/build/<variant>/vs-<other>.html, opened in the browser (a reworded bullet
sits on one row with only the changed words marked), and a plain vs-<other>.diff. Everything lands
in the gitignored resume/build/.
"""

from __future__ import annotations

import difflib
import html
import re
import subprocess
import sys
import urllib.request
import webbrowser
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "resume" / "build"
DEPLOYED_PDF = ROOT / "site" / "public" / "ankush-jain-resume.pdf"
LIVE_URL = "https://me.entertoescape.com/ankush-jain-resume.pdf"

BULLET = re.compile(r"^[•●‣⁃�]\s*")
PHONE = re.compile(r"\+?\d[\d\s-]{8,}\d")


def pdf_text(pdf: Path) -> str:
    """One logical line per bullet / heading / skill row."""
    raw = "\n".join(page.extract_text() for page in PdfReader(pdf).pages)
    lines: list[str] = []
    for line in raw.splitlines():
        # pypdf leaves a trailing space on a line that wrapped mid-sentence; a row that
        # wrapped after a comma (skills lists) loses it, so treat that as a wrap too
        # and a line starting lowercase is a continuation - except the contact row,
        # whose email address starts lowercase
        if lines and (lines[-1].endswith(" ") or lines[-1].endswith(",")
                      or (line[:1].islower() and "@" not in line)):
            lines[-1] = lines[-1].rstrip() + " " + line.strip()
        else:
            lines.append(line)
    out = []
    for line in lines:
        line = BULLET.sub("- ", line.rstrip())
        # the live PDF carries a phone number; keep it out of files on disk
        line = PHONE.sub("<phone>", line)
        out.append(line)
    return "\n".join(out) + "\n"


def render(variant: str) -> Path:
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "render_resume.py"), variant])
    if r.returncode != 0:
        sys.exit(f"ERROR: rendering {variant} failed")
    return BUILD / variant / "resume.pdf"


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    variant = args[0]

    if "--against" in flags:
        i = sys.argv.index("--against")
        other = sys.argv[i + 1]
        args = [a for a in args if a != other]
        other_name, other_pdf = other, render(other)
    elif "--live" in flags:
        other_name = "live"
        other_pdf = BUILD / "_live" / "resume.pdf"
        other_pdf.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(LIVE_URL, other_pdf)
    else:
        other_name, other_pdf = "deployed", DEPLOYED_PDF

    new_pdf = render(variant)

    old_txt = BUILD / f"_{other_name}" / "resume.txt" if other_name in ("deployed", "live") \
        else other_pdf.with_suffix(".txt")
    old_txt.parent.mkdir(parents=True, exist_ok=True)
    new_txt = new_pdf.with_suffix(".txt")
    old_txt.write_text(pdf_text(other_pdf), encoding="utf-8")
    new_txt.write_text(pdf_text(new_pdf), encoding="utf-8")

    base = ["git", "diff", "--no-index", "--unified=1"]
    if "--word" in flags:
        base.append("--word-diff=plain")
    rel = lambda p: str(p.relative_to(ROOT)).replace("\\", "/")
    paths = [rel(old_txt), rel(new_txt)]

    saved = BUILD / variant / f"vs-{other_name}.diff"
    plain = subprocess.run(base + ["--no-color"] + paths, cwd=ROOT,
                           capture_output=True, text=True, encoding="utf-8")
    saved.write_text(plain.stdout, encoding="utf-8")

    page = BUILD / variant / f"vs-{other_name}.html"
    page.write_text(side_by_side(old_txt.read_text(encoding="utf-8").splitlines(),
                                 new_txt.read_text(encoding="utf-8").splitlines(),
                                 other_name, variant), encoding="utf-8")

    if "--git" in flags:
        # exit code 1 from git diff just means "they differ"
        subprocess.run(base + ["--color=always"] + paths, cwd=ROOT)
    print(f"saved: {rel(page)}\nsaved: {rel(saved)}")
    if "--no-open" not in flags:
        webbrowser.open(page.as_uri())
    return 0


# --- side-by-side HTML view ------------------------------------------------------

def align(old: list[str], new: list[str]):
    """Rows of (old_line|None, new_line|None, kind). A reworded bullet pairs with its
    rewrite on one row instead of showing as an unrelated delete and insert."""
    rows = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
        if tag == "equal":
            rows += [(old[i], new[j], "same") for i, j in zip(range(i1, i2), range(j1, j2))]
            continue
        a, b = old[i1:i2], new[j1:j2]
        j = 0
        for line in a:
            # pair with the next sufficiently similar line on the right, keeping order
            hit = next((k for k in range(j, len(b))
                        if difflib.SequenceMatcher(None, line, b[k]).ratio() >= 0.5), None)
            if hit is None:
                rows.append((line, None, "del"))
                continue
            rows += [(None, x, "add") for x in b[j:hit]]
            rows.append((line, b[hit], "mod"))
            j = hit + 1
        rows += [(None, x, "add") for x in b[j:]]
    return mark_moves(pair_singletons(rows))


def similar(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a, b).ratio()


def pair_singletons(rows):
    """A lone removed line directly followed by a lone added line is a rewrite of it,
    however different the words (the summary, a retitled header)."""
    out, i = [], 0
    while i < len(rows):
        r = rows[i]
        if (r[2] == "del" and i + 1 < len(rows) and rows[i + 1][2] == "add"
                and (i + 2 == len(rows) or rows[i + 2][2] != "add")
                and (not out or out[-1][2] != "del")):
            out.append((r[0], rows[i + 1][1], "mod"))
            i += 2
        else:
            out.append(r)
            i += 1
    return out


def mark_moves(rows):
    """A removed line that reappears elsewhere (possibly reworded) was moved, not cut."""
    dels = [i for i, r in enumerate(rows) if r[2] == "del"]
    adds = [i for i, r in enumerate(rows) if r[2] == "add"]
    rows = list(rows)
    for d in dels:
        best = max(adds, key=lambda a: similar(rows[d][0], rows[a][1]), default=None)
        if best is None or similar(rows[d][0], rows[best][1]) < 0.6:
            continue
        adds.remove(best)
        o, n = rows[d][0], rows[best][1]
        down = best > d
        rows[d] = (o, None, "movefrom", n, "moved down" if down else "moved up")
        rows[best] = (None, n, "moveto", o, "moved from above" if down else "moved from below")
    return rows


def words(a: str, b: str) -> tuple[str, str]:
    """Both sides as HTML, with only the changed words marked."""
    ta, tb = re.split(r"(\s+)", a), re.split(r"(\s+)", b)
    out_a, out_b = [], []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ta, tb, autojunk=False).get_opcodes():
        sa, sb = html.escape("".join(ta[i1:i2])), html.escape("".join(tb[j1:j2]))
        if tag == "equal":
            out_a.append(sa); out_b.append(sb)
        else:
            if sa.strip(): out_a.append(f"<del>{sa}</del>")
            if sb.strip(): out_b.append(f"<ins>{sb}</ins>")
    return "".join(out_a), "".join(out_b)


def is_heading(line: str) -> bool:
    # section titles, project and role lines - not bullets, the contact row,
    # skill rows or sentences
    return (not line.startswith("- ") and "|" not in line and ": " not in line
            and not line.rstrip().endswith(".") and len(line) < 90)


def side_by_side(old: list[str], new: list[str], old_name: str, new_name: str) -> str:
    rows = align(old, new)
    counts = {k: sum(1 for r in rows if r[2] == k) for k in ("mod", "add", "del", "moveto")}
    body = []
    for a, b, kind, *move in rows:
        if kind == "mod" and similar(a, b) >= 0.55:
            ha, hb = words(a, b)
        elif kind == "movefrom":
            ha, hb = words(a, move[0])[0] + f' <span class="badge">{move[1]}</span>', ""
        elif kind == "moveto":
            ha, hb = "", words(move[0], b)[1] + f' <span class="badge">{move[1]}</span>'
        else:
            # whole-line rewrites get a row tint, not a confetti of word highlights
            ha = html.escape(a) if a is not None else ""
            hb = html.escape(b) if b is not None else ""
        cls = kind + (" head" if is_heading(a if a is not None else b) else "")
        body.append(f'<tr class="{cls}"><td class="l">{ha}</td><td class="r">{hb}</td></tr>')
    return PAGE.format(old=html.escape(old_name), new=html.escape(new_name),
                       mod=counts["mod"], add=counts["add"], dele=counts["del"], moved=counts["moveto"],
                       rows="\n".join(body))


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Resume diff: {old} vs {new}</title>
<style>
:root {{ --bg:#fff; --fg:#1f2328; --muted:#8a9099; --line:#e6e8eb;
  --del-bg:#ffebe9; --del-hi:#ffc1bc; --add-bg:#e6ffec; --add-hi:#abf2bc; --empty:#f6f8fa;
  --move-bg:#eef4ff; --move-fg:#0b57d0; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#0d1117; --fg:#e6edf3; --muted:#7d8590;
  --line:#21262d; --del-bg:#3c1618; --del-hi:#7d2a2a; --add-bg:#12301c; --add-hi:#1f6b35; --empty:#161b22;
  --move-bg:#14233d; --move-fg:#79a6ff; }} }}
* {{ box-sizing:border-box }}
body {{ margin:0; background:var(--bg); color:var(--fg);
  font:14px/1.5 -apple-system, "Segoe UI", Calibri, Arial, sans-serif; }}
header {{ position:sticky; top:0; background:var(--bg); border-bottom:1px solid var(--line);
  padding:12px 16px; display:flex; gap:16px; align-items:baseline; flex-wrap:wrap; z-index:1 }}
header h1 {{ font-size:16px; margin:0 }}
.stat {{ color:var(--muted) }} .stat b {{ color:var(--fg) }}
label {{ margin-left:auto; color:var(--muted); cursor:pointer }}
table {{ width:100%; border-collapse:collapse; table-layout:fixed }}
th {{ text-align:left; padding:8px 16px; font-size:13px; color:var(--muted);
  border-bottom:1px solid var(--line) }}
td {{ vertical-align:top; padding:3px 16px; border-bottom:1px solid var(--line); word-wrap:break-word }}
td.l {{ border-right:1px solid var(--line) }}
tr.same td {{ color:var(--muted) }}
tr.head td {{ font-weight:600; padding-top:10px }}
tr.same.head td {{ color:var(--fg) }}
tr.del td.l, tr.mod td.l {{ background:var(--del-bg) }}
tr.add td.r, tr.mod td.r {{ background:var(--add-bg) }}
tr.del td.r, tr.add td.l, tr.movefrom td.r, tr.moveto td.l {{ background:var(--empty) }}
tr.movefrom td.l, tr.moveto td.r {{ background:var(--move-bg) }}
.badge {{ font-size:11px; color:var(--move-fg); border:1px solid currentColor; border-radius:9px;
  padding:0 6px; margin-left:6px; white-space:nowrap }}
del {{ background:var(--del-hi); text-decoration:none; border-radius:2px }}
ins {{ background:var(--add-hi); text-decoration:none; border-radius:2px }}
body.changes tr.same:not(.head) {{ display:none }}
</style></head>
<body>
<header><h1>{old} &rarr; {new}</h1>
<span class="stat"><b>{mod}</b> reworded &middot; <b>{add}</b> added &middot; <b>{dele}</b> removed &middot; <b>{moved}</b> moved</span>
<label><input type="checkbox" id="only"> changes only</label></header>
<table><thead><tr><th>{old}</th><th>{new}</th></tr></thead><tbody>
{rows}
</tbody></table>
<script>document.getElementById('only').onchange=e=>document.body.classList.toggle('changes',e.target.checked)</script>
</body></html>
"""


if __name__ == "__main__":
    raise SystemExit(main())
