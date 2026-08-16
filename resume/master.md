# Ankush Jain

**Senior Backend Engineer**

> Master resume — the complete record, no page limit. This is the reference
> document and is never sent to an employer as-is. One-page tailored versions
> are generated from it via `scripts/render_resume.py`.

> Generated from `content/career.json`. Edit that file, not this one.

---

## Contact

- **Github:** https://github.com/ankushsio
- **Linkedin:** https://www.linkedin.com/in/ankush-jain-22313a20/
- **Website:** https://me.entertoescape.com
- **Email:** kushjaing@gmail.com
- **Location:** Bengaluru, India

## Summary

Backend engineer with ~5 years building distributed systems for regulated healthcare and imaging - EHR integration, cloud infrastructure, access control, and AI/ML pipelines. Comfortable owning a system end to end: high- and low-level design, implementation, security hardening, and the CI/CD that ships it.

## Positioning

- **Level:** senior backend engineer
- **Experience:** ~5 years (graduated 2021)
- **Seeking:** A role with real ownership and systems depth, at a company worth staying at for years.

**Themes:**

- Distributed backends in regulated domains (healthcare, clinical research, medical devices)
- Systems integration - EHR/FHIR, message brokers, event-driven services
- Security and access control - RBAC, auth hardening, static-analysis remediation
- Performance and delivery engineering - pipeline and image-size optimization, CI/CD
- Applied research to production - imaging, signal processing, AI/OCR

---

## Experience

### Apra Labs — Senior Software Engineer
*May 2023 – Present*

Engineering services company. Work is delivered for external clients across healthcare, medical devices and imaging; clients are not named. Also contributed to Apra Labs' own products and open source.

#### Clinical Trial Management Platform
*Nov 2024 – Present · Clinical research / healthcare · Backend engineer - integration, cloud infrastructure, access control*

A multi-service platform connecting clinical trial study teams and participants to hospital electronic health record systems. My longest-running project and the one where I moved from writing features to shaping design.

**Problem.** Trial data lives inside hospital EHR systems that each expose different APIs, standards and quirks. Every new data source risked becoming a bespoke integration, and a platform handling patient data needed access control and auditability that could survive scrutiny - neither of which existed when I joined.

**Approach.** Built the integration hub's base adapter modules so that every new EHR adapter follows one predictable shape, then implemented the first EHR adapter as the reference others were built from. Moved inter-service communication onto managed pub/sub with asynchronous subscriptions, dead-letter handling and retry logic. Wrote infrastructure as code for the cloud APIs, serverless service instances, topics and subscriptions. Designed and implemented role-based access control across both the study-team and participant applications - identifying admin-only endpoints, filtering responses per role, and adding pre-authorization checks for resources a user cannot reach. Added server-sent events for real-time feedback, hardened authentication, remediated static-analysis findings, and rebuilt the CI/CD pipelines.

**Outcome.** Phase 1 delivered on schedule. Deployments got meaningfully faster, container images meaningfully smaller, and the platform gained an access-control story it previously lacked.

**Highlights**

- Cut the backend deployment pipeline from 26 min 33 s to 18 min 07 s (-32%), shortening every developer's feedback loop `[metric]`  
  <sub>source: eval:2026-04</sub>
- Designed and shipped a full role-based access control system across two applications, covering admin and basic access - admin-only endpoint restriction, per-role response filtering, and pre-authorization checks  
  <sub>source: eval:2025-11</sub>
- Built the integration hub's base adapter modules, turning each new EHR integration from a bespoke build into a repeatable pattern; implemented the first adapter as the reference implementation  
  <sub>source: eval:2025-05</sub>
- Re-architected inter-service connectivity on managed pub/sub with async subscriptions, dead-letter handling and retry enhancement  
  <sub>source: eval:2026-04</sub>
- Wrote infrastructure as code for cloud APIs, serverless instances, topics and subscriptions, making environment setup reproducible  
  <sub>source: eval:2025-05</sub>
- Reduced a service container image from 450 MB to 290 MB (-36%) by eliminating unneeded dependencies while clearing technical debt `[metric]`  
  <sub>source: timesheet:2025-02</sub>
- Eliminated $200+/month of idle cloud spend (~$2.4k/year) by auditing and decommissioning legacy services, and set up billing review to catch it earlier `[metric]`  
  <sub>source: eval:2025-05 + eval:2026-04</sub>
- Remediated security findings from static analysis reports and led a security overhaul separating study-team and participant application concerns  
  <sub>source: eval:2025-11</sub>
- Introduced server-sent events for real-time product feedback, a pattern later adopted by other teams in the organization  
  <sub>source: eval:2026-04</sub>
- Delivered phase 1 features end to end: diagnostics smoke tests, participant deletion APIs, retry enhancements, build-info endpoints and integration test updates  
  <sub>source: eval:2026-04</sub>
- Mapped business entitlements into an enterprise identity flow federated with Microsoft Entra, enforcing endpoint security and data-level response filtering through JWT claims  
  <sub>source: resume-draft</sub>
- Migrated the GCP sandbox environment onto the client's internal cloud with no loss of service  
  <sub>source: resume-draft</sub>

**Tech:** Java, Spring Boot, Kotlin, Ktor, Go, Google Cloud Pub/Sub, Cloud Run, Terraform, FHIR / HAPI, Docker, Server-Sent Events, RBAC, Microsoft Graph API, Flyway, GraalVM, Gradle, Microsoft Entra, JWT


#### AR Surgical Navigation
*Aug 2023 – Apr 2024 · Medical devices / augmented reality · Engineer - 3D pipeline, performance, team lead in practice*

A research system reconstructing 3D anatomy from intra-operative video for augmented-reality surgical guidance. I took it from a file-based research prototype toward something that could run in real conditions.

**Problem.** The reconstruction pipeline wrote intermediate results to disk between every stage, which made it slow and fragile. Worse, a signed distance field computation ran per frame and bottlenecked the entire operation - no amount of tuning elsewhere mattered while it dominated the frame budget.

**Approach.** Read the literature and open-source implementations to understand the geometry properly, then migrated the file-based pipeline to in-memory - which meant understanding every module's inputs and outputs and refactoring the connections between them. For the bottleneck, I worked out that the signed distance field did not need recomputing per frame and devised a technique to compute it once and reuse it. Added multi-inference passes, multi-mesh views, error calculation, and robustness across different input data types.

**Outcome.** Removed the dominant per-frame cost, cutting more than 80% of the time it consumed. Onboarded two junior engineers onto the project and led it through a period when senior engineers were unavailable.

**Highlights**

- Cut end-to-end pipeline latency from 22s to 2s by moving the reconstruction pipeline from file-based I/O to in-memory and eliminating a per-frame signed distance field computation that dominated the frame budget `[metric]`  
  <sub>source: eval:2024-05 + resume-draft</sub>
- Refactored module boundaries and data flow across the reconstruction pipeline to make the in-memory migration possible  
  <sub>source: eval:2023-11</sub>
- Shipped pipeline features weekly - multi-inference passes, multi-mesh views, error calculation, and robust handling of varied input data  
  <sub>source: eval:2023-11</sub>
- Onboarded two junior engineers and led the project through a stretch when senior engineers were unavailable, having become its most familiar contributor  
  <sub>source: eval:2024-05</sub>
- Brought graphics and geometry knowledge into a team new to it, sharing VTK and 3D fundamentals through internal brainstorming sessions  
  <sub>source: eval:2023-11</sub>
- Optimised inference by converting PyTorch models to ONNX and TensorRT, cutting per-frame model execution time  
  <sub>source: resume-draft</sub>
- Solved perspective and alignment problems in the 3D organ model so reconstructed anatomy rendered correctly against the live view  
  <sub>source: resume-draft</sub>

**Tech:** C++, Python, VTK, 3D meshes & point clouds, Signed distance fields, Neural reconstruction, Computer vision, PyTorch, ONNX, TensorRT


#### Headless Video Recording Platform
*Apr 2024 – Oct 2024 · Video infrastructure / edge computing · Backend engineer - C++ and Node services, state, real-time*

An Apra Labs network video recorder running headless on edge devices. Built on ApraPipes, the company's open-source video and image processing pipeline framework. I joined when it was unstable and worked on getting it to a dependable state.

**Problem.** The recorder was in an unstable state - segmentation faults in the decoder, unreliable behaviour across edge hardware, and no coherent story for how the C++ core, the web layer and the UI shared state.

**Approach.** Refactored the C++ backend and wrote the Node backend from scratch, then made Redis the single source of ground truth connecting them and the frontend. Integrated server-sent events for real-time notifications, which unlocked a set of features that polling could not serve well. Added proper logging across both the C++ and Node sides - which is what finally made the intermittent decoder crashes diagnosable rather than guessable. Debugged segmentation faults in frame decoding and tested aggressively across edge device targets.

**Outcome.** Brought the platform from unstable to a dependable state and integrated the previously disconnected modules into one controllable system with consistent state.

**Highlights**

- Took the recorder from an unstable state to a dependable one, debugging intermittent segmentation faults in frame decoding across edge hardware  
  <sub>source: eval:2024-05</sub>
- Wrote the Node backend from scratch, managing the lifecycle of the C++ binaries and carrying inter-process communication over Redis key-value and Pub/Sub, so the whole system shared one source of truth  
  <sub>source: eval:2025-05</sub>
- Integrated server-sent events for real-time notifications, enabling functionality that polling could not serve cleanly  
  <sub>source: eval:2025-05</sub>
- Built proper logging across both the C++ and Node backends, converting intermittent, hard-to-reproduce crashes into diagnosable failures  
  <sub>source: eval:2025-05</sub>
- Integrated the previously separate modules with fine-grained control and correct handling of edge cases, with ground truth maintained in Redis  
  <sub>source: eval:2025-05</sub>

**Tech:** C++, Node.js, Redis, hiredis, redis-plus-plus, Server-Sent Events, ApraPipes, NVIDIA Jetson (AGX/NX), Video decoding, OpenCV

- [ApraPipes (Apra Labs open source, C++)](https://github.com/Apra-Labs/ApraPipes)

#### Document AI / Handwriting Recognition Pipeline
*May 2025 – Nov 2025 · Applied AI / document processing · Engineer and designer - end-to-end system, owned HLD and LLD*

An end-to-end system turning scanned handwritten documents into structured data, built around a licensed third-party handwriting-recognition model. The first project where I owned both the high- and low-level design.

**Problem.** The recognition model came as a large third-party artifact with a time-limited licence. Wrapping it naively would have produced an enormous deployment, coupled our code to someone else's release cycle, and made licence renewal a redeployment emergency.

**Approach.** Took the vendor's model and code, worked out how it actually functioned, and adapted it to our use case until there was a working end-to-end system. Then designed the codebase so it packages and deploys alongside the model with the licence swappable on expiry rather than baked in. Set up a RabbitMQ message broker connecting the document pipeline to the partner backend, adding the features and usability the integration needed. Produced the high- and low-level design independently with minimal supervision.

**Outcome.** Cut the deployable image from 19 GB to 5.28 GB - a 72% reduction - and delivered the system within its timeline. My design reviews and guidance then enabled the team to build the LLM-based successor.

**Highlights**

- Reduced the deployable image from 19 GB to 5.28 GB (-72%) through deliberate packaging design `[metric]`  
  <sub>source: eval:2025-11</sub>
- Designed the codebase so the third-party model packages and deploys with the system and its licence can be swapped on expiry, instead of requiring a rebuild  
  <sub>source: eval:2025-11</sub>
- Took an unfamiliar vendor model and codebase to a working end-to-end AI system adapted to our use case  
  <sub>source: eval:2025-11</sub>
- Produced the high- and low-level design independently with minimal supervision  
  <sub>source: eval:2025-11</sub>
- Built out the RabbitMQ message broker connecting the document pipeline to the partner backend  
  <sub>source: eval:2025-11</sub>
- Reviewed code and design and guided the team, enabling them to build the LLM-based successor system  
  <sub>source: eval:2025-11</sub>

**Tech:** Python, Docker, RabbitMQ, Handwriting recognition (HTR/OCR), System design (HLD/LLD), Message brokers


#### Regenerative Medicine Data Platform
*May 2026 – Present · Healthcare data / clinical standards · Engineer - architecture, FHIR modelling, AI-assisted delivery*

Current project. A FHIR-native platform for clinical protocols and surveys, modelled on healthcare terminology standards, being migrated off a legacy application. My work here is as much architecture and requirements as implementation.

**Problem.** A legacy application needed replacing with something modelled properly on healthcare standards rather than ad-hoc structures, with requirements arriving as slide decks, whiteboard sessions and client calls rather than as a spec.

**Approach.** Modelled protocols, surveys and their relationships on FHIR resources, using OMOP and LOINC terminology so questions map to recognized clinical codes rather than free text. Implemented change logs purely through FHIR provenance. Built a question bank explorable against the standard terminology. Researched SMART on FHIR to decide where the access-control layer belonged, and produced a permission matrix across roles. Drove requirements directly with the client - turning whiteboard discussions into wireframed workflows and user stories, then iterating on their feedback. Used AI-assisted and agent-orchestrated development throughout for legacy-to-new UI migration and phased implementation, supervising and correcting the output rather than accepting it.

**Outcome.** Delivered phased implementations against a product plan, ran client demos, and shifted the project's requirements from ambiguous discussions to wireframed workflows with explicit user stories.

**Highlights**

- Modelled clinical protocols and surveys on FHIR resources with OMOP/LOINC terminology, and implemented change logs purely through FHIR provenance  
  <sub>source: timesheet:2026-06</sub>
- Built a question bank letting users explore questions against standard clinical terminology instead of free-text entry  
  <sub>source: timesheet:2026-06</sub>
- Produced a permission matrix across roles and researched SMART on FHIR to determine the correct layer for access control  
  <sub>source: timesheet:2026-07</sub>
- Drove requirements with the client directly - converting whiteboard sessions and slide feedback into wireframed workflows and user stories  
  <sub>source: timesheet:2026-07</sub>
- Used AI-assisted and agent-orchestrated development for legacy-to-new migration and phased delivery, supervising and correcting output rather than accepting it  
  <sub>source: timesheet:2026-05</sub>
- Simplified environment setup so a new developer needs only the source and terminology files, with everything else provisioned automatically  
  <sub>source: timesheet:2026-06</sub>

**Tech:** FHIR, OMOP, LOINC, SMART on FHIR, RBAC, Docker Compose, Playwright, AI-assisted development, Requirements & architecture design


#### Retinal Video Biomarker Research
*Jun 2023 – Sep 2023 · Medical imaging / signal processing · Research engineer*

Applied-research work extracting a physiological signal from retinal video - establishing whether a usable signal was present at all before anyone built a product on the assumption.

**Problem.** Retinal video is noisy and subject to motion; it was an open question whether a reliable pulse signal could be recovered from it, and which region of the frame carried it.

**Approach.** Read the underlying papers and open-source implementations, then experimented across different frame regions, pixel-value conditions, histograms and illumination to find where correlation actually held. Built an image-registration pipeline producing stable, registered video, and worked in the frequency domain using FFT/DFT to extract beats-per-minute values from the registered signal.

**Outcome.** Established the presence of a valid physiological signal and produced a working registration pipeline. The image-registration code was durable enough to be revived and reused on a new image set nearly two years later.

**Highlights**

- Implemented published algorithms to extract beats-per-minute from retinal video, establishing that a valid physiological signal was present  
  <sub>source: eval:2023-11</sub>
- Built an image-registration pipeline producing stable registered video, after experimenting across frame regions to find where correlation held  
  <sub>source: eval:2023-11</sub>
- Wrote the registration code well enough that it was revived and applied to a different image set nearly two years later  
  <sub>source: timesheet:2025-06</sub>

**Tech:** Python, Computer vision, Image registration, FFT/DFT, Signal processing, Research literature


#### Hyperspectral Imaging Analysis
*Aug 2024 – Oct 2024 · Medical imaging / early disease indicators · Research engineer - camera, tooling, pipeline*

Establishing hyperspectral imaging capability from scratch: standing up the camera, learning the domain, and leaving behind a library and pipeline the team could actually use.

**Problem.** Nobody on the team had used a hyperspectral camera. Captured images came out faint under our lighting, and it was unclear whether that was the room, the calibration procedure, or a misunderstanding of what the data meant.

**Approach.** Read the research on hyperspectral imaging for early disease indicators, set up the camera physically with measured positioning, and worked through lighting conditions until images were usable - the breakthrough being that calibration captures had been misread as needing extra brightness. Wrote a helper library on top of the camera SDK providing region-of-interest selection, cleaning and preprocessing for downstream analysis, plus a data-generation pipeline covering feature extraction, brightness extraction, and normalization against a dark reference.

**Outcome.** Turned an unfamiliar instrument into a documented, repeatable capability - camera setup, helper library, data pipeline and written documentation for teams in other locations.

**Highlights**

- Wrote a helper library over the camera SDK for region-of-interest selection, cleaning and preprocessing of captured spectral data  
  <sub>source: eval:2025-05</sub>
- Set up the hyperspectral camera and worked out the lighting and calibration conditions that produced usable captures, then shared the know-how with the team  
  <sub>source: eval:2025-05</sub>
- Built a data-generation pipeline covering feature extraction, brightness extraction and dark-reference normalization  
  <sub>source: timesheet:2024-09</sub>
- Documented the setup and workflow for a team in another location to reproduce  
  <sub>source: timesheet:2024-09</sub>

**Tech:** Python, Jupyter, Hyperspectral imaging, Spectral calibration, Feature extraction, NumPy, Data pipelines


#### Access Control & Security Platform
*Jun 2023 – Jul 2023 · Physical security / access control · Engineer - serialization migration, reliability*

My first project. Migrating a command protocol off protobuf and hardening how the service handled malformed input.

**Problem.** Commands arrived in batches, and a single bad command could take down processing for the whole batch. The system also carried protobuf serialization that was being retired.

**Approach.** Migrated commands and tests from protobuf to gzip and removed the leftover artifacts, verifying the service stayed stable without them. Made command processing resilient so one bad command no longer prevented the rest of the batch from being handled, and worked through schema and command dependency issues alongside the testing team.

**Outcome.** Completed the serialization migration and made batch command processing fault-tolerant rather than all-or-nothing.

**Highlights**

- Migrated commands and tests from protobuf to gzip and removed the retired artifacts, verifying service stability afterwards  
  <sub>source: eval:2023-11</sub>
- Made batch command processing resilient so one malformed command no longer blocked the remaining commands in the batch  
  <sub>source: timesheet:2023-06</sub>

**Tech:** protobuf, gzip, Debian packaging, Schema design, Access control domain


#### Across projects

- Onboarded and mentored junior engineers across multiple projects, and served as a tech buddy for new joiners  
  <sub>source: eval:2026-04</sub>
- Conducted technical interviews for the company  
  <sub>source: eval:2025-11</sub>
- Spread server-sent events and message-broker patterns across teams; both are now used by multiple teams and people  
  <sub>source: eval:2026-04</sub>
- Regular code, design and pair-review contributor across teams, including for projects outside my own  
  <sub>source: eval:2026-04</sub>
- Presented internal tech talks, including one on federated learning  
  <sub>source: eval:2025-05</sub>

### Earlier roles

- **ByteLearn** — Software Engineer (May 2022 – Apr 2023)
- **Deloitte USI** — Business Technical Analyst (Software Developer) (Sep 2021 – May 2022)
- **Utopia Global, Inc.** — Machine Learning Intern (Jan 2021 – Jun 2021)
- **Innovaccer** — Data Science Intern (May 2020 – Jul 2020)
- **Directi** — Workshop Trainer Intern (May 2019 – Jun 2019)

---

## Skills

- **Languages:** Python, C++, Java, Kotlin, Go, JavaScript/Node.js, TypeScript
- **Backend:** Spring Boot, Ktor, REST APIs, Server-Sent Events (SSE), RabbitMQ, Google Cloud Pub/Sub, Event-driven architecture, Flask
- **Databases:** PostgreSQL, SQL, Redis, Flyway (migrations)
- **Cloud Devops:** Google Cloud Platform (GCP), Cloud Run, AWS (Lambda, Step Functions), Terraform, Docker, CI/CD pipelines, Infrastructure as code (IaC), Observability (Sentry, Graylog)
- **Domain:** HL7 FHIR, OMOP, LOINC, SMART on FHIR, EHR integration, Clinical trial systems
- **Security:** Role-based access control (RBAC), Authentication & authorization, OAuth / token-based auth, Microsoft Graph API, Static analysis remediation, Microsoft Entra, JWT
- **Ml Imaging:** Computer vision, Image registration, Signal processing (FFT/DFT), Hyperspectral imaging, OCR / handwriting recognition, VTK, PyTorch, ONNX, TensorRT
- **Practices:** High- and low-level design, Code review, Mentoring, Technical interviewing, AI-assisted development, Requirements gathering

## Education

- **Dr. SPM IIIT Naya Raipur** — B.Tech, Computer Science and Engineering (2017 – 2021)

## Personal projects

### EnterToEscape
*2026-06 – present*

A browser game I built and ship myself, live on my own domain. Written in TypeScript with Phaser, deployed as a Cloudflare Worker serving static assets plus a leaderboard API backed by D1, with CI on every push and preview URLs per branch.

*The one project I can hand someone the source for. It is also where I own the whole stack - game loop, backend, database, auth, deployment pipeline and DNS.*

**Tech:** TypeScript, Phaser, Vite, Cloudflare Workers, Cloudflare D1, Google OAuth, CI/CD

- [Play](https://entertoescape.com)
- Source: https://github.com/ankushsio/entertoescape *(repo is private — not linked publicly)*
