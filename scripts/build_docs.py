"""
Generate the long-form master resume and the LinkedIn copy from content/career.json.

    python scripts/build_docs.py

Writes:
    resume/master.md          everything, no page limit -- the reference document
    linkedin/headline.txt     220 char limit
    linkedin/about.txt        2,600 char limit
    linkedin/experience-senior.txt    2,000 char limit (Senior SWE, May 2026 - present)
    linkedin/experience-engineer.txt  2,000 char limit (SWE, May 2023 - May 2026)
    linkedin/projects/*.txt   per-project blurbs for the Projects section

LinkedIn strips markdown, so those files are plain text with bullet characters and real
line breaks. Character limits are asserted, not assumed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAREER = ROOT / "content" / "career.json"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

LIMITS = {"headline": 220, "about": 2600, "experience": 2000, "project": 2000}


def fmt(ym: str | None, fallback: str = "Present") -> str:
    if not ym:
        return fallback
    y, m = ym.split("-")[:2]
    return f"{MONTHS[int(m) - 1]} {y}"


def span(period: dict) -> str:
    return f"{fmt(period['start'])} – {fmt(period.get('end'))}"


# ---------------------------------------------------------------- master resume

def master_resume(c: dict) -> str:
    person, company = c["person"], c["companies"][0]
    prior = c.get("prior_experience", {})
    out: list[str] = []

    out += [
        f"# {person['name']}", "",
        f"**{person['title']}**", "",
        "> Master resume — the complete record, no page limit. This is the reference",
        "> document and is never sent to an employer as-is. One-page tailored versions",
        "> are generated from it via `scripts/render_resume.py`.", "",
        "> Generated from `content/career.json`. Edit that file, not this one.", "",
        "---", "", "## Contact", "",
    ]
    for key, value in person["links"].items():
        out.append(f"- **{key.title()}:** {value}")
    out += [f"- **Email:** {person['email']}", f"- **Location:** {person['location']}", ""]

    out += ["## Summary", "", person["summary"], "",
            "## Positioning", "",
            f"- **Level:** {c['positioning']['level']}",
            f"- **Experience:** ~{c['positioning']['years_experience']} years "
            f"(graduated {c['positioning']['graduated']})",
            f"- **Seeking:** {c['positioning']['seeking']}", "",
            "**Themes:**", ""]
    out += [f"- {t}" for t in c["positioning"]["themes"]]
    out += ["", "---", "", "## Experience", "",
            f"### {company['name']} — {company['role']}",
            f"*{fmt(company['start'][:7])} – {fmt(company.get('end'))}*", "",
            company["context"], ""]

    for p in company["projects"]:
        out += [f"#### {p['title']}",
                f"*{span(p['period'])} · {p['domain']} · {p['role']}*", "",
                p["summary"], "",
                f"**Problem.** {p['problem']}", "",
                f"**Approach.** {p['approach']}", "",
                f"**Outcome.** {p['impact']}", "",
                "**Highlights**", ""]
        for h in p["highlights"]:
            mark = " `[metric]`" if h.get("metric") else ""
            out.append(f"- {h['text']}{mark}  \n  <sub>source: {h['source']}</sub>")
        out += ["", f"**Tech:** {', '.join(p['tech'])}", ""]
        for link in p.get("links", []):
            out.append(f"- [{link['label']}]({link['url']})")
        out.append("")

    out += ["#### Across projects", ""]
    out += [f"- {h['text']}  \n  <sub>source: {h['source']}</sub>"
            for h in company["cross_project_highlights"]]
    out.append("")

    full_time = prior.get("full_time", [])
    internships = prior.get("internships", [])
    if full_time or internships:
        out += ["### Earlier roles", ""]
        for job in full_time + internships:
            out.append(f"- **{job.get('company', '?')}** — {job.get('role', '?')} "
                       f"({job.get('dates', '?')})")
        out.append("")
    else:
        out += ["### Earlier roles", "",
                "> **TODO — blocked on the current CV.** Two full-time engineering roles",
                "> (2021–2023) and three internships (pre-2021), plus education.", ""]

    out += ["---", "", "## Skills", ""]
    for key, items in c["skills"].items():
        out.append(f"- **{key.replace('_', ' ').title()}:** {', '.join(items)}")
    out.append("")

    education = c.get("education", {})
    out += ["## Education", ""]
    if isinstance(education, list) and education:
        out += [f"- **{e['institution']}** — {e['degree']} ({e['dates']})"
                for e in education]
    else:
        out.append("> **TODO — blocked on the current CV.** Degree, institution, "
                   "graduation year (2021).")
    out.append("")

    out += ["## Personal projects", ""]
    for p in c["personal_projects"]:
        out += [f"### {p['title']}", f"*{p['period']['start']} – "
                f"{p['period'].get('end') or 'present'}*", "", p["summary"], "",
                f"*{p['why_it_matters']}*", "",
                f"**Tech:** {', '.join(p['tech'])}", ""]
        for link in p["links"]:
            if p.get("repo_is_private") and link["label"] == "Source":
                out.append(f"- {link['label']}: {link['url']} "
                           f"*(repo is private — not linked publicly)*")
            else:
                out.append(f"- [{link['label']}]({link['url']})")
        out.append("")

    return "\n".join(out)


# ------------------------------------------------------------------- linkedin

def linkedin_headline(c: dict) -> str:
    return ("Senior Software Engineer at Apra Labs | Distributed systems, event-driven "
            "architecture, access control | Java/Kotlin, Python, GCP")


def linkedin_about(c: dict) -> str:
    company = c["companies"][0]
    lines = [
        "I build backends for systems where being wrong is expensive.",
        "",
        "For the last three years at Apra Labs that has meant service integration, "
        "event-driven architecture, access control and the delivery pipelines that ship "
        "them - mostly in settings where a mistake is costly: clinical trials, surgical "
        "imaging, video infrastructure running on edge hardware. Before that, two "
        "engineering roles and three internships after graduating in 2021.",
        "",
        "What I tend to do on a project:",
        "",
        "• Turn one-off integrations into a repeatable pattern - I built the base "
        "adapter modules for an integration hub so each new service connection "
        "follows one shape instead of becoming a bespoke build.",
        "• Design and ship access control properly - a full RBAC system, covering "
        "admin-only endpoints, per-role response filtering and "
        "pre-authorization checks.",
        "• Find the cost nobody has looked at - a per-frame computation that dominated "
        "a 3D reconstruction pipeline (over 80% of its time removed), a 19 GB "
        "deployable cut to 5.28 GB, a deploy pipeline taken from 26m33s to 18m07s, "
        "$200+/month of idle cloud spend found and decommissioned.",
        "• Own design end to end - high- and low-level design, then the implementation, "
        "security hardening and CI/CD that ships it.",
        "",
        "I work mostly in Java/Kotlin, Python, Node and C++, on GCP, with Pub/Sub, "
        "RabbitMQ, Redis, PostgreSQL, Docker and Terraform. I also spend real time on the things "
        "around the code: onboarding people, reviewing designs rather than only diffs, "
        "and making project setup simple enough that a new developer needs the source "
        "and nothing else.",
        "",
        "Client work is described without naming clients.",
        "",
        "Portfolio: me.entertoescape.com",
    ]
    return "\n".join(lines)


def linkedin_experience_senior(c: dict) -> str:
    """Senior Software Engineer, May 2026 - present.

    LinkedIn gives every position under the same employer its own description box, so
    the promotion buys a second ~2,000 character budget instead of five projects
    competing for one. The single entry was sitting at 1,935 of 2,000.

    The split is also the accurate one rather than merely convenient: every
    clinical-trial highlight carries a `source` evaluation dated before May 2026, so
    that work belongs to the earlier role even though the project is still running.
    """
    return "\n".join([
        "Engineering services across healthcare, medical devices and imaging. "
        "Clients are not named.",
        "",
        "MEDICINE DATA PLATFORM (May 2026 - present)",
        "• Modelled clinical protocols and surveys on FHIR resources with OMOP/LOINC "
        "terminology; implemented change logs purely through FHIR provenance.",
        "• Produced a permission matrix across roles to settle where the access-control "
        "layer belonged.",
        "• Built a question bank explorable against the standard terminology.",
        "• Drove requirements with the client, turning whiteboard sessions into "
        "wireframed workflows and E2E implementation.",
        "• Used AI-assisted and agent-orchestrated development for legacy-to-new UI "
        "migration and phased delivery, supervising and correcting the output rather "
        "than accepting it.",
    ])


def linkedin_experience_engineer(c: dict) -> str:
    """Software Engineer, May 2023 - May 2026. Everything up to the promotion."""
    return "\n".join([
        "Engineering services across healthcare, medical devices and imaging. "
        "Clients are not named.",
        "",
        "CLINICAL TRIAL MANAGEMENT PLATFORM (Nov 2024 - present)",
        "• Built the integration hub's base adapter modules, turning each new "
        "integration from a bespoke build into a repeatable pattern; implemented the "
        "reference adapter.",
        "• Designed and shipped a full role-based access control system - "
        "admin-only endpoint restriction, per-role response filtering, "
        "pre-authorization checks.",
        "• Re-architected inter-service connectivity on GCP Pub/Sub with async "
        "subscriptions, dead-letter handling and retries; wrote the Terraform for it.",
        "• Cut the backend deploy pipeline from 26m33s to 18m07s and a service image "
        "from 450 MB to 290 MB.",
        "• Eliminated $200+/month of idle cloud spend by auditing and decommissioning "
        "legacy services, and set up billing review to catch the next one.",
        "",
        "DOCUMENT AI / HANDWRITING RECOGNITION (May - Nov 2025)",
        "• Owned high- and low-level design of an end-to-end OCR system around a "
        "licensed third-party model.",
        "• Designed packaging so the model ships with the system and its licence can be "
        "swapped on expiry; cut the deployable from 19 GB to 5.28 GB.",
        "",
        "HEADLESS VIDEO RECORDING PLATFORM (Apr - Oct 2024)",
        "• Wrote the Node backend from scratch and made Redis the single ground truth "
        "shared with the C++ core; added SSE for real-time updates.",
        "• Took the recorder from unstable to dependable, debugging intermittent "
        "segmentation faults across edge hardware.",
        "",
        "AR SURGICAL NAVIGATION (Aug 2023 - Apr 2024)",
        "• Identified a signed distance field computation as the pipeline bottleneck "
        "and devised a compute-once-and-reuse technique, removing over 80% of the time "
        "it took per frame.",
        "• Migrated the reconstruction pipeline from file-based to in-memory; onboarded "
        "two junior engineers.",
    ])


def linkedin_project(p: dict) -> str:
    parts = [p["title"], "", p["summary"], "", "What I did:", p["approach"], "",
             "Outcome:", p["impact"], "", f"Tech: {', '.join(p['tech'])}"]
    return "\n".join(parts)


def check(name: str, text: str, limit: int) -> bool:
    ok = len(text) <= limit
    flag = "OK  " if ok else "OVER"
    print(f"  {flag} {name:34s} {len(text):5d} / {limit}")
    return ok


def main() -> int:
    career = json.loads(CAREER.read_text(encoding="utf-8"))

    (ROOT / "resume").mkdir(exist_ok=True)
    (ROOT / "resume" / "master.md").write_text(master_resume(career), encoding="utf-8")
    print("wrote resume/master.md")

    ln = ROOT / "linkedin"
    (ln / "projects").mkdir(parents=True, exist_ok=True)

    print("\nLinkedIn character limits:")
    all_ok = True
    pieces = [
        ("headline.txt", linkedin_headline(career), LIMITS["headline"]),
        ("about.txt", linkedin_about(career), LIMITS["about"]),
        # One box per position. The May 2026 promotion means LinkedIn shows two entries
        # under Apra Labs, each with its own limit.
        ("experience-senior.txt", linkedin_experience_senior(career), LIMITS["experience"]),
        ("experience-engineer.txt", linkedin_experience_engineer(career), LIMITS["experience"]),
    ]
    for filename, text, limit in pieces:
        (ln / filename).write_text(text, encoding="utf-8")
        all_ok &= check(filename, text, limit)

    for p in career["companies"][0]["projects"]:
        text = linkedin_project(p)
        (ln / "projects" / f"{p['slug']}.txt").write_text(text, encoding="utf-8")
        all_ok &= check(f"projects/{p['slug']}.txt", text, LIMITS["project"])

    if not all_ok:
        print("\nFAIL: at least one block exceeds its LinkedIn limit — trim it.")
        return 1
    print("\nAll blocks within LinkedIn limits.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
