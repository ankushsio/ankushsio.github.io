# Changes to the Apra Labs role — RESOLVED AND APPLIED (2026-08-17)

This was the approval gate for the current role. Everything below came from four resume drafts;
`career.json` for Apra Labs otherwise derives from timesheets and self-evaluations, which are
contemporaneous records rather than later recollection. **All decisions are now applied.**

## Outcome

| Item | Decision |
|---|---|
| A1 · AR latency | **22s → 2s end-to-end**, with the SDF fix stated as the mechanism |
| A2 · Cloud cost | One recurring saving: **$200+/month (~$2.4k/year)**, basis shown so the figure is checkable |
| B1 · ONNX / TensorRT | Added |
| B2 · Microsoft Entra federation, JWT claims | Added |
| B3 · GCP sandbox → client internal cloud | Added |
| B4 · 3D organ model perspective | Added |
| B5 · C++ binary lifecycle + Redis IPC | Merged into the recorder highlight |
| B6 · "account revenue growth" | **Dropped** — revenue attribution invites a question that cannot be won |
| B7 · 99.9% uptime | **Dropped** — no evidence, trivially challenged |
| B8 · Kubernetes | **Dropped** — one draft, absent from three years of timesheets |
| B9 · Django / FastAPI / MongoDB / MySQL / GCS / S3 / Bash | **Dropped**; Flask added (real, from ByteLearn) |
| C1 · "Senior Software Engineer" | **Not used** — title stays Software Engineer; the work reads senior on its own |
| C2 · Location | Bengaluru, India |
| C3 · Phone | **PDF only**, never on the public site (verified in the build) |

### Note on annualised figures

The $200/month → $2.4k/year derivation is legitimate because the saving is *recurring and
measured*: a decommissioned idle service does not come back. What draws scrutiny is annualising
an unmeasured or one-off figure, where the multiplier magnifies the error as well as the number.
Stating the monthly basis alongside the annual total answers that objection before it is raised.

---

## Original analysis (kept for the record)

---

## A. Conflicts — I need your ruling

### A1. AR Surgery latency: "22s → 2s (90%)" vs "over 80% of per-frame time"

| Source | Claim |
|---|---|
| Self-eval 2023–24 (in `career.json` now) | The signed distance field computation was the bottleneck; computing it once instead of per frame saved **"more than 80% of time per frame"** |
| Resume drafts (2 of 4) | **"reducing latency by 90% (from 22s to 2s)"** for real-time organ deformation viewing |

**These may not actually conflict.** The eval measures one computation; the drafts measure the
whole pipeline end to end, after both the in-memory migration *and* the SDF fix. Both can be
true at once.

**My recommendation:** use the end-to-end number as the headline, because it is what a reader
cares about, and keep the SDF detail as the mechanism:

> Cut end-to-end pipeline latency from 22s to 2s by migrating the reconstruction pipeline from
> file-based I/O to in-memory and eliminating a per-frame signed distance field computation that
> dominated the frame budget.

**Confirm:** is 22s → 2s a real measurement you stand behind, and does it describe the whole
pipeline rather than the SDF step alone?

### A2. Cloud cost: "$200+" vs "thousands of dollars annualised"

| Source | Claim |
|---|---|
| Self-eval 2024–25 (in `career.json` now) | "Identified the high cloud cost and informed the team, **saved the project more than $200**" |
| Resume draft | "Audited and decommissioned legacy services, eliminating redundant cloud waste and **saving thousands of dollars in annualized operational costs**" |

These are a real gap — 10× or more apart. Two readings: they are **two separate events** (the
2024–25 spot saving, and a later, larger decommissioning that appears in the 2025–26 eval as
the sandbox billing overwatch item), or the draft is an annualised projection of the
same saving.

**My recommendation:** if they are separate events, state both plainly. If "thousands" is a
projection from a monthly figure, say so ("~$X/month of idle spend, decommissioned") rather than
an annualised total — projected annual figures are the first thing an interviewer probes.

**Confirm:** one event or two? And is the larger number measured or projected?

---

## B. Additions — new material not in any timesheet or eval

| # | Claim from drafts | My read | Recommend |
|---|---|---|---|
| B1 | Converted PyTorch models to **ONNX / TensorRT** for faster inference (AR surgery) | Specific and technical, appears in 2 drafts. Nothing contradicts it — inference optimisation just would not show up in a timesheet line | **Add** |
| B2 | Federated enterprise identity with **Microsoft Entra**; authorization via **JWT claims** | `career.json` currently says "Microsoft Graph API" from the eval. Entra federation is a bigger, more senior claim | **Add if accurate** |
| B3 | Migrated the GCP sandbox environment **to the client's internal cloud** | Consistent with the eval's "sandbox billing overwatch" but the migration itself is new | **Add** |
| B4 | Solved **3D organ model perspective problems** | Specific, matches the VTK/graphics work | **Add** |
| B5 | Managed the **lifecycle of C++ binaries** from Node, IPC over Redis Pub/Sub | Sharper than the current "Redis as ground truth" phrasing — better engineering detail | **Merge into the existing NVR highlight** |
| B6 | Primary technical **SME for the AR surgery client, contributing to account revenue growth** | Revenue attribution is not something you can evidence in an interview, and it invites a question you cannot win | **Drop the revenue half**, keep "technical SME" |
| B7 | Ensured **99.9% uptime** | No supporting evidence anywhere, and uptime claims are trivially challenged | **Drop** |
| B8 | **Kubernetes** in the skills list | Appears in exactly one draft; nothing in three years of timesheets mentions it | **Drop unless you have used it** |
| B9 | Django, Flask, FastAPI, MongoDB, MySQL, GCS, S3, Bash | Flask is real (ByteLearn). The rest look aspirational or academic | **Add Flask only** |

---

## C. Positioning questions

| # | Issue | Recommend |
|---|---|---|
| C1 | Drafts self-describe as **"Senior Software Engineer with 5 years"**; your actual title is Software Engineer | Keep the title accurate. Seniority should come from the work described, not a self-applied label a recruiter can check |
| C2 | Apra Labs location: drafts say both **"Bengaluru, India"** and **"Remote"** | Pick one and I will use it everywhere |
| C3 | Phone number appears in all four drafts | **PDF résumé yes, public website no** — a phone number on a public page is a spam magnet, and the site already has email |
| C4 | Second email `ankush00jain@gmail.com` | Ignore; using `kushjaing@gmail.com` as you specified |

---

## D. Still missing — RESOLVED

**The three internships** were supplied separately (Utopia Global, Innovaccer, Directi) and
are on the Path and Résumé pages. They are not on the one-page PDF, where they would
displace stronger material.

**Student projects** (Quiz Platform, Accident Detection with HRRN, Math Assistant backend) exist
in one draft and as GitHub repos. You previously said personal work should be EnterToEscape only,
so I have left them out — say the word if that has changed now that they have context.
