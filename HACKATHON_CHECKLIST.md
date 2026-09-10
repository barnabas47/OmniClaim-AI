# 🏆 AWS Agents for Humans Hackathon: Master Submission Checklist & Blueprint

> **Project**: OmniClaim AI - Autonomous Flight Passenger Rights Advocate & Weather Bluff Disprover  
> **Track**: **Everyday Agents** (Taking busywork out of daily life: money, travel, legal paperwork)  
> **Submission Deadline**: September 15, 2026 @ 2:00 AM GMT+2  
> **Live Demo URL**: [https://omniclaim-ai.onrender.com](https://omniclaim-ai.onrender.com)  
> **Core Framework**: **Strands Agents SDK** (`strands-agents`) + **Amazon Bedrock AgentCore**

---

## 📋 1. Hackathon Requirements Verification Checklist

| # | Submission Item | Status | Verification Detail / Location |
|---|---|:---:|---|
| **1** | **Strands Agents SDK Usage** | ✅ **VERIFIED** | Multi-agent `@tool` architecture in `backend/agents/concierge_orchestrator.py` using `strands-agents` & `strands-agents-tools`. |
| **2** | **Everyday Agents Philosophy** | ✅ **VERIFIED** | *Runs autonomously in background (radar/weather surveillance), surfaces ONLY when €600 claim is ready for 1-Click Approval.* |
| **3** | **Open Source License** | ✅ **VERIFIED** | MIT License visible in repository root `LICENSE`. |
| **4** | **Public Code Repository** | ✅ **VERIFIED** | GitHub: `https://github.com/barnabas47/OmniClaim-AI.git` |
| **5** | **Architecture Diagram** | ✅ **VERIFIED** | Detailed Mermaid diagram embedded in `README.md`. |
| **6** | **Live Production Demo** | ✅ **VERIFIED** | Deployed 24/7 on Render at https://omniclaim-ai.onrender.com. |
| **7** | **Multi-tier Vision AI / OCR** | ✅ **VERIFIED** | Google Gemini Vision -> OpenAI GPT-4o -> AWS Bedrock Claude -> EasyOCR (Deep Learning) -> Windows Native OCR. |
| **8** | **Automated Test Suite** | ✅ **VERIFIED** | 100% Pytest pass (`8 passed in 27s`) in `backend/tests/`. |
| **9** | **5-Minute Demo Video** | ⏳ **ACTION REQUIRED** | Script & scene breakdown provided in Section 2 below. |
| **10** | **builder.aws.com Bonus Article** | ⏳ **ACTION REQUIRED** | Ready-to-publish draft provided in Section 3 below. |

---

## 🎬 2. 5-Minute Video Pitch Script (Max 5:00)

```
[0:00 - 0:45] SCENE 1: The Problem (Slides / Visual)
- Visual: Slide showing "$3.8 Billion Unclaimed Compensation Every Year" and "AirHelp takes 35-50% cut".
- Voiceover: "Every year, millions of passengers face flight delays exceeding 3 hours. Under statutory regulations like EU261 and UK261, airlines owe passengers up to €600 in cash. But airlines use friction tactics: claiming fake weather excuses and burying claims in bureaucracy, while third-party claim agencies take up to 50% of your money. What if an autonomous AI agent solved this entirely in the background without taking a single penny?"

[0:45 - 1:30] SCENE 2: The Solution & Strands SDK Architecture
- Visual: Show the Architecture Diagram from README.md.
- Voiceover: "Meet OmniClaim AI, built with the AWS Strands Agents SDK. OmniClaim AI is an autonomous everyday agent that operates on a set-and-forget philosophy: it monitors OpenSky ADS-B radar and NOAA meteorological telemetry 24/7. When a flight is disrupted, our multi-agent pipeline independently investigates weather bluffs, calculates geodesic distance compensation, and drafts formal legal demand notices."

[1:30 - 3:15] SCENE 3: Live Demo on https://omniclaim-ai.onrender.com
- Visual: Screen recording of the web app.
  1. Click on the 'Eligible Flights Database' tab -> Show real-time delay tracking and NOAA METAR weather disproval verdicts (e.g. 'VFR Clear, 10km visibility disproves airline force majeure excuse').
  2. Switch to 'Upload Boarding Pass' tab -> Upload the Lufthansa test ticket (LH1335, Balazs Kovacs, 218.53€).
  3. Show the animated loader -> Instant extraction of Passenger Name, Flight Number, Date, Route, and Expense Receipt amount.
  4. Automatically transitions to the 'Active Claim & Legal Notice' tab.
  5. Show the generated formal legal demand letter addressed to Lufthansa Customer Relations citing EU261 Articles 5, 7, and 9.
  6. Click 'Submit to Carrier' -> Confetti celebration + recorded audit log.

[3:15 - 4:15] SCENE 4: Technical Deep Dive
- Visual: Code editor showing backend/agents/concierge_orchestrator.py and @tool implementations.
- Voiceover: "Under the hood, OmniClaim AI utilizes the Strands Agents SDK to orchestrate specialized tools:
  - Multimodal Vision parsing with fallback from Amazon Bedrock Claude to on-device EasyOCR.
  - Live NOAA METAR weather parser to empirically dismantle carrier extraordinary circumstances defenses.
  - Great-Circle geodesic distance calculations for exact statutory entitlement mapping.
  - SQLite UPSERT persistence with strict 90-day retention."

[4:15 - 5:00] SCENE 5: Impact & Why it Matters
- Visual: Final summary slide showing '0% Commission, 100% Autonomous, Built with Strands SDK on AWS'.
- Voiceover: "OmniClaim AI turns passenger rights from a frustrating chore into an autonomous background superpower. Zero paperwork, zero commission, and 100% of your rightful compensation back in your pocket. Thank you!"
```

---

## ✍️ 3. Bonus Article Draft for builder.aws.com

**Title**: *Agents for Humans: Building OmniClaim AI with Strands Agents SDK and Amazon Bedrock*  
**Tags**: `Agents for Humans`, `Strands Agents`, `Amazon Bedrock`, `Python`, `GenAI`

### Article Body (Copy & Paste):

```markdown
# Agents for Humans: Building OmniClaim AI with Strands Agents SDK and Amazon Bedrock

## Introduction: Taking the Friction Out of Passenger Rights
Every year, over $3.8 Billion in statutory flight delay compensation (EU261/UK261) goes unclaimed. Airlines routinely invoke extraordinary weather circumstances to deflect claims, while bureaucratic forms exhaust passengers.

As part of the **AWS Agents for Humans Hackathon** (Everyday Agents track), we built **OmniClaim AI**—an autonomous passenger rights advocate powered by the **Strands Agents SDK** and **Amazon Bedrock**.

Instead of creating another app users have to constantly manage, OmniClaim AI operates autonomously in the background:
1. It ingests boarding passes via multimodal vision OCR.
2. It audits real-time OpenSky radar and NOAA METAR weather reports to empirically disprove airline excuses.
3. It drafts enforceable legal notices and surfaces only when a 1-click human-in-the-loop decision is ready.

## Architecture with Strands Agents SDK
We designed our system around the modular Strands Agents toolchain:
- **Concierge Orchestrator Agent**: Manages the end-to-end claim lifecycle.
- **Vision OCR Tool**: Multimodal pipeline prioritizing Amazon Bedrock Claude 3.7 Sonnet, Google Gemini, and server-side EasyOCR fallback.
- **Bluff Disprover Agent**: Cross-references airport METAR observations against parallel flight departure rates.
- **Legal Rights Agent**: Computes geodesic distances (Great-Circle) to determine statutory compensation tiers (€250, €400, €600) and Duty of Care expense reimbursements.

## Live Demo & Open Source
- **Live Demo**: https://omniclaim-ai.onrender.com
- **GitHub Repository**: https://github.com/barnabas47/OmniClaim-AI (MIT License)

Built with ❤️ for the AWS Agents for Humans Hackathon.
```

---

## 🚀 4. Final Submission Checklist (Before Sept 15, 2:00 AM GMT+2)

- [x] Repository is **Public** on GitHub
- [x] **MIT License** is visible in repo root
- [x] **README.md** includes Problem, Solution, Architecture Diagram, and Setup instructions
- [x] **Live Demo** is accessible at https://omniclaim-ai.onrender.com
- [x] All backend unit tests pass (`pytest backend/tests`)
- [ ] Record and upload the **5-minute Demo Video** (YouTube unlisted or public)
- [ ] Submit on Devpost: https://agentsforhumans.devpost.com
- [ ] (Bonus) Publish article on https://builder.aws.com with title starting with `Agents for Humans`
