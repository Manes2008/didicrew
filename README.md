# VideoCrew Studio — AI Creative Director & Media Automation Engine

[![Python Version](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15.0-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![OpenSpace Ecosystem](https://img.shields.io/badge/OpenSpace-Cloud_v2-8A2BE2?style=for-the-badge)](https://github.com/HKUDS/OpenSpace)
[![Playwright](https://img.shields.io/badge/Playwright-Automation-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev)
[![Docker Ready](https://img.shields.io/badge/Docker-Container_Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)

> **An Autonomous Scriptwriting, Art Direction, and Media Production Orchestration Platform powered by Next-Gen Agentic Intelligence.**

VideoCrew Studio bridges the gap between human cinematic intuition and hyperscale AI rendering infrastructure. Operating as **The AI Showrunner**, the platform solves the foundational flaw of contemporary AI media generation: **transforming robotic, hollow scripts into emotionally gripping narratives with audience retention engineering, psychological triggers, and 1-click automated ingestion into Google Flow (Veo & Voiceover Studio)**.

---

## 1. System Paradigm & Vision

Most existing AI video generators focus solely on pixel generation, producing generic, soulless videos with severe drop-offs within the first 3 seconds. VideoCrew Studio pivots entirely to the **Creative Director & Cognitive Core**:

* **Cinematic Directing & Retention Engineering**: Implements Hollywood and top-tier creator frameworks (Paradoxical Hooks, statistical contrast, curiosity loops), calculating precise speech cadence (~3.0 - 3.3 words/second) synchronized with TTS audio constraints.
* **OpenSpace Cloud Collective Intelligence**: Dynamically injects 16 specialized skills from HKUDS OpenSpace, eradicating formulaic AI cliches and enforcing strict production rubrics.
* **Symbiosis with Big Tech Compute**: Instead of straining local hardware with heavy rendering, VideoCrew outputs pixel-perfect Director Blueprints and uses a headless Playwright bridge to drive Google Flow's enterprise Veo and Imagen 3 compute engines automatically.

---

## 2. Competitive Matrix

| Evaluation Dimension | General AI Tools / Raw Flow Prompting | VideoCrew Studio Pipeline |
| :--- | :--- | :--- |
| **First 3s Retention Hook** | Non-existent; generic, sluggish openings | Automated Pattern A/B Hook generation |
| **Dialogue Speech Cadence** | Rigid pacing; overflow audio sync errors | Calibrated pacing (~3.0 words/s) for short-form video |
| **Video Visual Prompting** | Basic text; frequent safety filter rejections | 35mm cinematic lens specs, lighting, camera blocking |
| **Quality Audit & Verification** | Manual human review required | Autonomous Agent Content Quality Auditor rubric |
| **Google Flow Execution** | Laborious manual copy-pasting of every scene | 1-Click Playwright Automation Bridge |
| **Production Workspace** | Fragmented developer interfaces | Next.js 15 Dark Media Studio UI |

---

## 3. The 8-Stage Production Pipeline

The architecture sequences production through 8 specialized stages:

```
[ RAW CREATIVE SEED ]
         │
         ▼
[ Stage 1: Strategy & Ideation ] ────► (OpenSpace: content-strategy & gap-analysis)
         │
         ▼
[ Stage 2: Script & 3s Hook ] ───────► (OpenSpace: cinematic-script-writer & viral-video)
         │
         ▼
[ Stage 3: Content Audit ] ──────────► (OpenSpace: content-quality-auditor)
         │
         ▼
[ Stage 4: 6-Column Storyboard ] ────► (OpenSpace: storyboard & visual-vocabulary)
         │
         ▼
[ Stage 5: Art Direction & Camera ] ─► (OpenSpace: visual-prompt-engine & style-cards)
         │
         ▼
[ Stage 6: Data Sanitizer ] ─────────► (Clean VO tags, enforce <120 chars, strip --ar)
         │
         ▼
[ Stage 7: Playwright Automation ] ──► (Automated browser bridge into Google Flow)
         │
         ▼
[ PRODUCTION BLUEPRINT & VEO VIDEO CLIPS ]
```

---

## 4. Integrated 16 OpenSpace Studio Skills

The system loads expert instructions directly from the `skills/` directory synchronized from OpenSpace Cloud:

### Category A: Screenwriting & Narrative Strategy
- `cinematic-script-writer`: Crafts cinematic scripts calibrated for pacing, visual beats, and 3-second retention hooks.
- `storyboard`: Structures exhaustive 6-column production storyboards (Visual, Voiceover, Text, SFX/BGM).
- `content-quality-auditor`: Validates, scores, and auto-corrects narrative quality against strict retention rubrics.
- `viral-video-analysis`: Decodes platform engagement algorithms and weaves behavioral call-to-action triggers.
- `content-strategy`: Establishes core messaging pillars, audience personas, and positioning.
- `content-gap-analysis`: Identifies untapped informational voids across existing competitor media.
- `content-refresher`: Restructures legacy topics into novel, high-engagement angles.

### Category B: Visual Concept & Art Direction
- `visual-prompt-engine`: Translates script beats into high-fidelity cinematic video generation prompts.
- `visual-concept`: Constructs coherent moodboards, color palettes, and recurring visual motifs.
- `best-image-generation`: Optimizes material textures, volumetric lighting, and aspect composition.
- `blip-2-vision-language`: Maintains character consistency and subject recognition across scene cuts.

### Category C: Audio Conductor & Voice AI
- `elevenlabs-tts`: Calibrates expressive inflection, natural pauses, and conversational tone.
- `audio-conductor`: Coordinates master gain, dynamic sound effects (SFX), and background music (BGM).
- `audiocraft-audio-generation`: Generates rhythmic acoustic beds tailored to video cadence.
- `audio-processing`: Handles post-production dynamic compression, noise filtering, and EQ balancing.

### Category D: Video Motion & Camera Blocking
- `eachlabs-video-generation`: Optimizes camera motion vectors for modern diffusion video models.
- `hyperframes`: Controls frame transition continuity and visual momentum between cuts.

---

## 5. Google Flow Automation Bridge (Playwright)

VideoCrew Studio features a dedicated automation bridge connecting directly to Google Flow (`flow.google.com`):

1. **Intelligent Data Sanitizer**:
   - Strips speaker tags (`[NARRATOR]:`, `[DIALOGUE]:`) and word count metrics (`*(11 words)*`) to prevent speech synthesizers from uttering metadata.
   - Enforces strict character limits: Automatically chunks dialogue into phrases under **120 characters** (hard limit of Google Flow Voiceover Studio).
   - Strips legacy Midjourney flags (such as `--ar 9:16`) from Veo visual prompts.
   - Maps acoustic profiles automatically: **Alnilam** (solemn historical/epic), **Charon** (analytical/tech), **Achird** (approachable/lifestyle).

2. **Isolated Chrome Profile Architecture (`.chrome_profile`)**:
   - Operates on a dedicated, isolated Chromium instance, preventing lockfile collisions with personal browsing sessions.
   - Google Flow credentials are authenticated once; the automation engine preserves authenticated cookies indefinitely.

3. **1-Click Studio Workflow**:
   - Click **"Push to Google Flow"** directly on the Production Studio page to inspect the sanitized payload preview.
   - Trigger execution: Playwright navigates the project, injects scene prompts into the creation bar, and synthesizes matching voiceover clips in parallel.

---

## 6. Installation & Deployment Guide

### Prerequisites
- **Operating System**: Windows 10/11, macOS, or Linux
- **Python**: Version 3.12 or higher (Strict requirement for OpenSpace and Playwright)
- **Node.js**: Version 18+ (Required for Next.js 15 Frontend)
- **Database**: PostgreSQL 16+

### Method 1: Local Development Setup

1. **Clone the repository and prepare virtual environment**:
```bash
git clone https://github.com/Manes2008/didicrew.git
cd didicrew
python -m venv venv
venv\Scripts\activate  # On Linux/macOS: source venv/bin/activate
```

2. **Install Backend Dependencies**:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install --with-deps chromium
```

3. **Configure Environment Variables (`.env`)**:
```env
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
DATABASE_URL=postgresql+psycopg2://postgres:123456@localhost:5432/didicrew
OPENSPACE_API_KEY=your_openspace_key
GOOGLE_FLOW_PROJECT_URL=https://flow.google.com/project/your-project-id/tools
```

4. **Launch FastAPI Backend**:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

5. **Launch Next.js Studio Frontend**:
```bash
cd videocrew-ui
npm install
npm run dev
```
Open your browser at: `http://localhost:3000`

---

### Method 2: Docker Container Deployment

The stack is containerized for production on an optimized Python 3.12 base:

```bash
# Build and start all services via Docker Compose
docker compose up -d --build

# Or run the safe redeploy script (preserves database volumes)
scripts\redeploy.bat
```

> [!TIP]
> To launch an independent Chrome window dedicated to Google Flow for one-time authentication, simply execute:
> `scripts\start_flow_chrome.bat`

---

## 7. Repository Layout

```
videocrew/
├── config/
│   ├── agents.yaml             # AI Agent roles, goals, and backstories
│   └── tasks.yaml              # Production stage specifications and expected outputs
├── skills/                     # 16 native studio skills imported from OpenSpace Cloud
│   ├── mass-media/             # Narrative strategy, SEO, viral video mechanics
│   └── technology/             # Art direction, Veo visual prompts, TTS, audio design
├── src/
│   ├── api/v1/endpoints/       # FastAPI route controllers (Production, Config, Channels)
│   ├── core/
│   │   ├── engine.py           # WorkflowEngine orchestrating dynamic skill injection
│   │   ├── llm_provider.py     # Provider supporting Gemini 3.8 Flash, OpenAI o3-mini
│   │   └── skill_loader.py     # Recursive skill loader with in-memory caching
│   └── tools/
│       ├── google_flow_sanitizer.py # Data cleaner for dialogue and Veo prompts
│       ├── google_flow_bridge.py    # Playwright headless/headful automation engine
│       └── image_tool.py            # Local & cloud image engine (Flux Realism, Gemini)
├── videocrew-ui/               # Next.js 15 Dark Studio Interface (TailwindCSS)
├── scripts/
│   ├── redeploy.bat            # Safe Docker container recreation script
│   ├── start_flow_chrome.bat   # Dedicated Chrome browser launcher for Google Flow
│   └── sync_openspace.py       # Cloud synchronization utility for OpenSpace skills
├── Dockerfile                  # Production Python 3.12 container with Playwright deps
├── docker-compose.yml          # Service orchestration (Backend + PostgreSQL 16)
└── requirements.txt            # System dependencies pinned for Python 3.12+
```

---

## 8. License & Intellectual Property

This project is licensed under the terms of the **MIT License**.
Copyright (c) **2026 Manes2008/didicrew**. All rights reserved.
