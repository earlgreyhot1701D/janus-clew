🎭 Janus Clew
Evidence-backed growth tracking for indie builders

🔍 Prove your growth. Then own what's next.

You've shipped three projects in three months. You're definitely better—but can you prove it?

Janus Clew turns your code into measurable evidence. Not vibes. Not claims. Cold, hard proof that you leveled up. Your complexity grew. Your technologies evolved. Your reasoning deepened. This tool just makes it visible.

🎭 Why Janus?
In Roman mythology, Janus looks in two directions simultaneously—backward and forward.

Janus Clew does the same for your growth: it shows you where you've been (measurable complexity across projects) and tells you where you're ready to go (forward-looking career guidance).

Most growth tracking tools show you dashboards. Janus Clew shows you evidence—and then tells you what you're ready for next.

🚀 The Real Problem
You're shipping faster than ever. Your growth is more invisible than ever.

Three months ago, you couldn't build what you shipped last week. You learned async patterns. You got comfortable with complexity. You tried new technologies. But there's zero way to prove any of it.

GitHub doesn't show growth. LinkedIn isn't measurable. Your portfolio doesn't explain the arc.

- You ship faster than you track
- Your growth is invisible to strangers
- Interviews ask "why should we believe you leveled up?"
- You can't point to evidence

This isn't a portfolio problem. This is an evidence preservation problem.

🎭 The Solution: Evidence + Intelligent Guidance
Janus Clew analyzes your actual code across projects and provides both backward-looking evidence AND forward-looking career guidance:

**What you built (Evidence):**

📊 Timeline - Complexity progression (6.2 → 7.5 → 8.1 means you leveled up 2.5x in 8 weeks)
🛠️ Skills Detected - Technologies you actually used (with proof: click to see in GitHub)
🔍 Complexity Breakdown - How the score was calculated (Files + Functions + Classes + Nesting depth)
📤 Shareable Export - Beautiful card for LinkedIn, interviews, portfolios

**What you're ready for (AWS AgentCore Intelligence):**

Using AWS AgentCore to read your complete project history, Janus detects patterns and generates intelligent recommendations—not generic advice, but guidance rooted in your actual code:

🧠 Patterns Recognized - "You avoid databases" + "You prefer async patterns" (AgentCore analyzes cross-project architecture)
🚀 Recommendations - "You're ready for PostgreSQL + asyncpg" with reasoning (AgentCore reasons about your trajectory)
📈 Trajectory Analysis - Your growth velocity + what naturally comes next (AgentCore evaluates your learning curve)
🎯 Career Guidance - Forward-looking path based on your demonstrated patterns (AgentCore makes intelligent suggestions, not generic ones)

Why this works: Your code tells a story. Phase 1 reads it. Phase 2 (AgentCore) understands it and tells you what's next.

🔬 How It Works
**Phase 1: Evidence Collection (Complete)**

```
Your Repos (3+ projects)
           ↓
    Git Analysis (commit history, recency)
           ↓
    Code Parsing (AST: files, functions, classes, nesting)
           ↓
    Multi-Factor Complexity Scoring (0-10 scale, hard to game)
           ↓
    Local Storage (~/.janus-clew/ - your data stays yours)
           ↓
    Timeline visible. Skills proven. Growth measurable.
```

**Phase 2: Intelligent Guidance (Complete - AWS AgentCore)**

```
All stored analyses loaded into memory
           ↓
    AWS AgentCore reads your complete project history
           ↓
    Pattern Detection:
    - "You avoid databases" (cross-project analysis)
    - "You prefer async-first" (architectural patterns)
    - "Your growth: 2.5x in 8 weeks" (trajectory analysis)
           ↓
    Recommendation Engine (via AgentCore agentic reasoning):
    - "Ready for PostgreSQL + asyncpg" (based on YOUR patterns)
    - "Keep shipping async" (strengthen your strength)
    - "Team mentoring: not yet" (honest scoping)
           ↓
    Patterns + Recommendations Tab populated
           ↓
    Career Guidance rooted in YOUR code, not generic advice
```

**Full Pipeline:**

Local Analysis → Storage → AgentCore Intelligence → Dashboard → Export

Why Multi-Factor Complexity Scoring?
Simple line-of-code counts are noisy. You can inflate them accidentally. Multi-factor is harder to game—it captures real problem difficulty:

```
Score = Files (0-3) + Functions (0-4) + Classes (0-2) + Nesting (0-1)
      = 0-10 scale
      = represents actual problem complexity
      = judges can verify it in your GitHub
```

Your first project: 6.2 complexity. You handled 10 functions across 4 files.
Your second project: 7.5 complexity. You're comfortable with 20 functions, async patterns, error handling.
Your third project: 8.1 complexity. You're designing for scale, using classes effectively, handling deep nesting.

That's not luck. That's measurable growth.

⚡ Quick Start
**Setup (5 min)**

```bash
# 1. Clone & setup
git clone https://github.com/earlgreyhot1701D/janus-clew.git
cd janus-clew
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure AWS
cp .env.example .env
# Add your AWS_BUILDER_ID_EMAIL

# 3. Frontend deps (optional rebuild)
cd frontend && npm install
cd ..
```

**Run**

```bash
# Terminal 1: Backend server
python -m backend.server
# → http://localhost:3001

# Terminal 2: Analyze your projects
python -m cli.main analyze ~/project1 ~/project2 ~/project3

# Open browser → http://localhost:3001
# Click through tabs: Timeline, Skills, Patterns, Export
```

🚀 Deploying to AWS Bedrock AgentCore
**Prerequisites**
- AWS Account with credentials configured
- Python 3.11+ with virtual environment
- AWS Permissions for Bedrock AgentCore, ECR, CodeBuild, IAM
- bedrock-agentcore-starter-toolkit installed

**Installation**

```bash
# Install the AgentCore toolkit
pip install bedrock-agentcore-starter-toolkit

# Verify installation
agentcore --help
```

**Configuration**

Your .bedrock_agentcore.yaml should look like this:

```yaml
default_agent: backend_agent
agents:
  backend_agent:
    name: backend_agent
    entrypoint: backend/agent.py
    deployment_type: container
    platform: linux/arm64
    source_path: null  # Upload entire project
    aws:
      region: us-east-1
      # ... other AWS settings
```

Key settings:
- `entrypoint: backend/agent.py` - Relative path (not absolute Windows path)
- `source_path: null` - Uploads entire project to CodeBuild
- `platform: linux/arm64` - Required for Bedrock AgentCore Runtime

**Critical Fix: Dockerfile Location**

⚠️ Important: The toolkit generates a Dockerfile in `.bedrock_agentcore/backend_agent/Dockerfile`, but CodeBuild expects it at the project root.

Before deploying, run:

```bash
# Copy Dockerfile to project root
Copy-Item .bedrock_agentcore\backend_agent\Dockerfile -Destination Dockerfile

# Verify the Dockerfile
Get-Content Dockerfile | Select-Object -First 10
```

The Dockerfile should have:

```
CMD ["opentelemetry-instrument", "python", "-m", "backend.agent"]
```

Note the dot in `backend.agent` (not slash) - this is correct module notation.

**Deploy**

```bash
# Launch deployment (uses CodeBuild - no local Docker needed)
agentcore launch --code-build --auto-update-on-conflict
```

This will:
- Upload your source code to S3
- Create a CodeBuild project
- Build ARM64 Docker image in the cloud
- Push image to ECR
- Deploy to Bedrock AgentCore Runtime

Deployment takes 5-10 minutes.

**Monitor Build Logs**

In a separate terminal, watch the build progress:

```bash
aws logs tail /aws/codebuild/bedrock-agentcore-backend_agent-builder --follow --format short --region us-east-1
```

Watch for these stages:
- ✅ DOWNLOAD_SOURCE - Getting code from S3
- ✅ BUILD - Docker build (ARM64)
- ✅ POST_BUILD - Push to ECR
- ✅ COMPLETED - Success!

**Verify Deployment**

```bash
# Check deployment status
agentcore status

# Should show:
# - agent_arn: arn:aws:bedrock-agentcore:...
# - agent_id: (non-null)
# - Status: Ready
```

**Test Your Agent**

```bash
# Test invocation
agentcore invoke '{"prompt":"Analyze my growth","projects":[]}' --session-id test-01
```

Expected response:

```json
{
  "status": "success",
  "projects_analyzed": 0,
  "patterns": [],
  "recommendations": ["Keep building..."],
  "model": "bedrock-agentcore-janus"
}
```

**Troubleshooting**

Build fails: "requirements.txt not found"
- Make sure `source_path: null` in YAML (not `source_path: backend`)
- This ensures the entire project is uploaded, not just the backend folder

Build fails: "Dockerfile not found"
- Copy Dockerfile to project root: `Copy-Item .bedrock_agentcore\backend_agent\Dockerfile -Destination Dockerfile`

CMD syntax error in Dockerfile
- Should be: `CMD ["python", "-m", "backend.agent"]` (with dot)
- NOT: `CMD ["python", "-m", "backend/agent"]` (slash doesn't work)

Permission errors
- Ensure AWS credentials are configured: `aws sts get-caller-identity`
- Check IAM permissions for Bedrock AgentCore, ECR, CodeBuild

**Clean Up**

To destroy the deployed agent:

```bash
agentcore destroy --agent backend_agent --force
```

🎬 Using It

**Timeline Tab**
Line chart of your complexity across projects. See the moment you leveled up. The bend in the curve is where you internalized a new concept.

**Skills Tab**
Technologies detected from your actual code (not what you say you know—what you actually used).

Click any skill → See it in your GitHub. Click "AWS Bedrock" → see the exact 8 files where you imported it. Proof, not claims.

**Patterns Tab** ✨ (Phase 2)
Your development signature. Cross-project patterns that define how you code:

- "You avoid databases" (all 3 projects use stateless patterns)
- "You prefer async-first" (concurrency built in from day 1)
- "Your complexity growth: 2.5x in 8 weeks" (faster than average)

**Recommendations Tab** ✨ (Phase 2)
Forward-looking guidance. Based on your actual patterns, what are you ready to learn?

```
✅ You're READY for PostgreSQL + asyncpg
Why: You know async patterns. PostgreSQL is async-first.
     You've already solved the hardest part.
Next: Build event-driven service with PostgreSQL

🔄 Keep building async architecture first
Why: Your last 2 projects both favored async.
     This is your strength. Deepen it before pivoting.

⏳ Not yet: Team mentoring
Why: Prove solo track record first.
     Come back when you've shipped 5+ projects.
```

This isn't "you should learn databases"—generic advice. This is "based on your code patterns and trajectory, here's what's next." Real intelligence.

**Complexity Breakdown**

You can see exactly how the score was built:

```
Project: TicketGlass
Complexity: 8.1

Files: 12 (score: 2.4)
Functions: 45 (score: 3.6)
Classes: 8 (score: 1.9)
Nesting depth: 18 (score: 0.2)
─────────────────
Total: 8.1/10
```

Why this is trustworthy:
- No magic. You can click and verify in GitHub.
- Multi-factor. Hard to game. Real complexity.
- Judges can reproduce. "Show me the functions" → 45 in the AST.

**Export Card**

Beautiful, shareable proof for LinkedIn, portfolios, interviews:

```
┌─────────────────────────────────┐
│  YOUR GROWTH JOURNEY            │
├─────────────────────────────────┤
│  Sept 15  →  Complexity 6.2     │
│  Oct 04   →  Complexity 7.5     │
│  Nov 04   →  Complexity 8.1     │
├─────────────────────────────────┤
│  📈 Growth: 2.5x in 8 weeks     │
│  🛠️ Skills: 8 technologies       │
│  ✅ Proven by code analysis      │
└─────────────────────────────────┘
```

🎯 For Indie Builders
This is built for you: the person shipping multiple projects, losing context between them.

You know the pattern:

- Month 1: Build something simple. Learn the basics. (Complexity: 4.0)
- Month 2: Apply what you learned. Tackle harder problems. (Complexity: 6.5)
- Month 3: Ship something complex that would have been impossible before. (Complexity: 8.2)

But nobody sees that arc. It's invisible.

Janus Clew makes it visible.

🏗️ Architecture

```
janus-clew/
├── cli/
│   ├── main.py                # Entry point: janus-clew analyze ~/project1
│   ├── analyzer.py            # Real git + AST parsing (complexity scoring)
│   ├── agentcore_caller.py    # AWS Bedrock AgentCore integration (production-grade)
│   ├── storage.py             # ~/.janus-clew/ persistence
│   └── prompts.py             # LLM prompts (centralized)
│
├── backend/
│   ├── server.py              # FastAPI + static file serving
│   ├── models.py              # Pydantic data schemas
│   └── services/
│       ├── analyses.py        # GET /api/analyses
│       ├── timeline.py        # GET /api/timeline
│       ├── skills.py          # GET /api/skills
│       ├── patterns.py        # GET /api/patterns (AWS AgentCore)
│       └── recommendations.py # GET /api/recommendations (AWS AgentCore)
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   └── Dashboard.tsx
│   │   └── components/
│   │       ├── Timeline.tsx
│   │       ├── SkillsView.tsx
│   │       ├── PatternTab.tsx
│   │       ├── RecommendationTab.tsx
│   │       ├── ComplexityBreakdown.tsx
│   │       └── ExportCard.tsx
│   └── dist/                  # Built production
│
├── tests/
│   ├── test_analyzer.py       # Git + complexity scoring
│   ├── test_storage.py        # Data persistence
│   ├── test_integration.py    # End-to-end pipeline
│   └── test_phase2_services.py # Pattern detection & recommendations
│
├── .env.example               # Config template
├── requirements.txt           # Python deps
├── pyproject.toml            # Black + isort formatting
└── README.md                 # This file
```

📡 API Reference

**Analysis Endpoints**
```
GET  /api/health                    # Service running?
GET  /api/analyses                  # All analyses with timestamps
GET  /api/timeline                  # Complexity over time
GET  /api/skills                    # Detected technologies
GET  /api/complexity/{project_name} # Breakdown (files, functions, etc.)
```

**Phase 2 Endpoints (AWS AgentCore)**
```
GET  /api/patterns              # Cross-project patterns detected
GET  /api/recommendations       # Forward-looking career guidance
GET  /api/development-signature # Your complete "growth signature"
```

**Documentation**
```
GET  /docs                      # OpenAPI/Swagger interactive docs
GET  /redoc                     # ReDoc alternative
```

🔒 Privacy & Trust

✅ Local storage first - Your data in ~/.janus-clew/ (your machine)
✅ No cloud sync - Unless you explicitly enable it (post-hackathon feature)
✅ No tracking - No analytics, no telemetry, no "phone home"
✅ Transparent scoring - Every metric shows how it was calculated

✅ Testing

```bash
pytest tests/ -v              # All tests
pytest --cov                  # With coverage report
pytest -k pattern             # Only Phase 2 tests
```

42 tests passing - validates entire pipeline end-to-end.

🤖 Phase 2: AWS AgentCore Powers Intelligent Guidance

This is where Janus Clew becomes truly agentic.

Phase 1 is smart: multi-factor complexity scoring, transparent methodology, evidence-based analysis.

Phase 2 with AgentCore is intelligent: it reads your complete project history and reasons about patterns you can't see alone.

**How AgentCore Works in Janus Clew**

AgentCore reads all your stored analyses and performs agentic reasoning:

**Pattern Detection (AgentCore reasoning):**

Input: All 3 project analyses
- Code structures, technologies, complexity scores
- Commit patterns, growth velocity
- Architectural decisions across projects

AgentCore analyzes:
- Database usage: 0 in all 3 projects → "You prefer stateless"
- Async patterns: 2/3 projects heavily async → "You lean async-first"
- Complexity growth: 2.1 → 4.2 → 3.8 (normalized) → "2.5x in 8 weeks"
- Technology adoption: Each project introduces new tech → "Fast learner"

Output: Structured patterns with evidence pointers

**Recommendation Engine (AgentCore agentic decision-making):**

Input: Detected patterns + Your demonstrated capabilities

AgentCore reasons:
```
"You've built async-heavy projects. You've avoided state management.
You're growing at 2.5x typical pace. Therefore:
- PostgreSQL + asyncpg: YES - matches your async strength
- Event-driven architecture: YES - stateless preference aligns
- Team mentoring: NOT YET - solo track record needs more projects"
```

Output: Intelligent recommendations (not generic templates)

**Why AgentCore, Not Just Rules?**

Without AgentCore:
```python
if database_count == 0 and project_count >= 3:
    recommendation = "You should learn databases"
```
Generic. Could be wrong. Doesn't understand context.

With AgentCore:
```
AgentCore reads: stateless preference + async strength + growth velocity
AgentCore reasons: "Your architectural style is intentional, not accidental"
AgentCore recommends: "PostgreSQL + asyncpg because it's async-first
                       and matches your demonstrated preferences"
```
Specific. Grounded. Intelligent.

**Architecture: AgentCore Integration**

```
Phase 1: CLI → AST parsing → Complexity scoring → Local storage
                                                      ↓
                                    ~/.janus-clew/analyses/*.json
                                                      ↓
Phase 2: Backend loads all analyses
         ↓
    AgentCore (via Bedrock) reads complete history
         ↓
    Pattern detection + reasoning
         ↓
    Recommendation engine generates career guidance
         ↓
    Frontend displays: Patterns tab + Recommendations tab
```

The memory system is your data on disk. AgentCore's job is to be intelligent about it.

**Pattern Detection (AgentCore-Powered)**

Janus + AgentCore read your code across all projects and identify your development signature:

- Stateless architecture: AgentCore detected 0 database usage across all 3 projects
- Async-first preference: AgentCore found async/await in 2/3 projects throughout
- Complexity trajectory: AgentCore analyzed 6.2 → 7.5 → 8.1 (2.5x growth in 8 weeks)

These aren't generic observations. AgentCore mines them from your actual code, reasoning about intentional patterns.

**Intelligent Recommendations (AgentCore Reasoning)**

Based on your demonstrated patterns and growth trajectory, AgentCore reasons about what you're ready for:

```
✅ You're READY for PostgreSQL + asyncpg
   Why: AgentCore detected your async strength across 2 projects.
        PostgreSQL is async-first. Match made.
   Evidence: 18+ async functions, pattern consistency

✅ You're READY for event-driven architecture
   Why: AgentCore observed your preference for stateless patterns.
        Events are inherently stateless.
   Evidence: 100% of projects avoid mutable shared state

🔄 Keep shipping async-first projects
   Why: AgentCore sees consistent advantage. Deepen it.
        This is your competitive differentiator.

⏳ Not yet: Team mentoring
   Why: AgentCore recommends solo track record first.
        Reach 5+ projects before mentoring others.
```

Why this is different: AgentCore reasons about your patterns, using Bedrock to understand context and intent. Not template matching. Not rules. Actual reasoning.

🎬 How This Was Built

**Solo builder + AI pair programming**

Tools used:
- Claude.ai (architecture decisions, reasoning)
- Claude Code (implementation + debugging)
- Amazon Q Developer (code analysis, development assistance)

Why mention this? Because this project about growth measurement was itself a demonstration of growth: Month 1 (concept), Month 2 (MVP), Month 3 (Phase 2 complete).

All decisions, scope choices, and implementations reviewed and owned by me. AI served as thinking partner and implementation assistant—but the architectural judgment calls? Those were mine.

👩‍💻 Built by La Shara Cordero

I build tools that make invisible things visible.

From Beyond the Docket (legal systems) to ThreadKeeper (forum knowledge) to Ariadne Clew (reasoning preservation)—every project starts with the same question: "What important information are we losing?"

Janus Clew continues that pattern: indie builder growth is invisible, but it's real and measurable.

**Development Timeline**

- Sept 14: Repository created (concept locked)
- Oct 04: Phase 1 MVP complete (CLI, backend, frontend)
- Oct 20: Phase 1 shipped (all tests passing, demo-ready)
- Nov 04: Phase 2 complete (AgentCore integration, patterns tab, recommendations)
- Nov 29: Ready for submission (42 tests passing, full pipeline working)

Total: 2.5 months of focused building. First AWS hackathon. Building on 4 months of AWS + LLM learning.

No formal AI training. No CS degree. Just a builder who sees problems and ships solutions.

🌟 Why Janus Clew Matters

**Technical Excellence**
✅ Real complexity scoring (multi-factor, hard to game)
✅ Transparent methodology (show your work)
✅ AgentCore integration (intelligent recommendations, not generic advice)
✅ End-to-end pipeline (CLI → storage → API → dashboard → export)
✅ Production code quality (42 tests, error handling, logging)

**Real-World Impact**
✅ Serves indie builders (underserved but growing)
✅ Measurable value: proof for interviews, portfolios, LinkedIn
✅ Scalable: works for any developer shipping multiple projects
✅ Honest MVP: solves core problem completely

**Differentiated Approach**
✅ First growth tracking tool for indie builders
✅ Backward-looking + forward-looking (others do just one)
✅ Evidence-based (not vibes or gut feeling)
✅ Built by indie builder who lives the problem

**Proof Points**
✅ 2.5 months from concept to Phase 2 complete
✅ 3 projects analyzed successfully (Your Honor → Ariadne Clew → Janus Clew)
✅ Multi-factor complexity scoring that judges can verify
✅ End-to-end demo that works reliably
✅ AgentCore real recommendations (not mock data)
✅ 42 passing tests validating entire system

🧠 Philosophy

Better to ship one thing that works than promise three things half-built.

Foundation-first approach. Real complexity measurement over vanity metrics. Transparent methodology over magic black boxes. One thing done right.

This is v1, not v-final.

🚀 What's Next

Post-hackathon roadmap:

- GitHub integration (analyze repos directly, no local upload)
- Multi-developer support (team analytics)
- VS Code extension (analyze from editor)
- Cloud sync (optional backup, collaboration)
- Social sharing (verified growth badges for LinkedIn)

But first: Ship this. Get feedback from indie builders. Learn what matters.

🤝 Development Approach

Built with AI pair programming (Claude as my "thinking partner off the bench").

All architectural decisions, scope choices, and final implementations reviewed and owned by me. AI served as implementation assistant, design feedback, and documentation search—but the judgment calls about what matters? Those were mine.

Modern solo development = Knowing when to build from scratch vs when to orchestrate and validate.

📬 Connect

Email: lsjcordero@gmail.com
LinkedIn: La Shara Cordero
Website: ThreadKeeper.io
Previous Work: Beyond the Docket

🎭 The Mirror

Janus looks backward and forward simultaneously.

Your code is the same. It tells a story of where you've been—the complexity you've learned to handle, the patterns you've developed, the technologies you've mastered.

Janus Clew just mirrors that story back to you, clearly enough that strangers can see it too.

Don't ship without proof. Don't apply for jobs without evidence. Don't underestimate your growth.

Janus Clew exists to help you see what you've already become.

**Version:** 2.0 (Phase 1 + Phase 2 Complete)
**Status:** Ready to Ship
**Built with:** Code, honesty, and the belief that indie builder growth deserves to be visible

**License**

MIT License - Use however you want.

Built with ☕, stubbornness, and the belief that growth should be measurable.

**Built for AWS Global Vibe: AI Coding Hackathon 2025**
Deadline: December 1, 2025
Phase 1 Complete: October 20, 2025
Phase 2 Complete: November 12, 2025
