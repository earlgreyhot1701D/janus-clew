# 🧵 Janus Clew - Refactored Edition with Full React Dashboard

**Evidence-backed coding growth tracking with Amazon Q Developer**

Complete, production-ready solution for measuring your coding progress objectively across projects.

---

## 🚀 What's New in This Release

### ✅ Complete MVP - Phase 1 Done
- **Backend API:** FastAPI server with all endpoints implemented
- **React Dashboard:** Full-featured React TypeScript frontend
- **Dark Mode:** Toggle between light and dark themes
- **Responsive Design:** Works on mobile, tablet, and desktop
- **Export:** Share your growth as HTML or copy to clipboard
- **Mock Fallback:** Works offline with demo data

### ✅ Backend (100% Complete)
- CLI tool for repository analysis
- Amazon Q integration with retry logic
- Local storage system (~/.janus-clew/)
- Service layer architecture
- Error handling & logging
- Custom exception hierarchy

### ✅ Frontend (100% Complete)
- Timeline visualization (Recharts)
- Skills display with confidence levels
- Growth metrics dashboard
- Complexity breakdown
- Evidence-backed claims
- Beautiful UI with Tailwind CSS

### ✅ All Fixes Applied
- Critical bugs fixed
- All services implemented
- Tests updated and passing
- Engineering best practices integrated
- Documentation complete

---

## 📁 Project Structure

```
janus-clew/
├── cli/                    # Python CLI tool
│   ├── main.py
│   ├── analyzer.py
│   ├── aws_q_client.py
│   └── storage.py
├── backend/                # FastAPI server
│   ├── server.py
│   ├── services.py
│   ├── models.py
│   └── __main__.py
├── frontend/               # React TypeScript dashboard
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── index.css
│   │   ├── pages/
│   │   │   └── Dashboard.tsx
│   │   ├── components/
│   │   │   ├── Timeline.tsx
│   │   │   ├── SkillsView.tsx
│   │   │   ├── GrowthMetrics.tsx
│   │   │   └── ExportCard.tsx
│   │   └── services/
│   │       └── api.ts
│   ├── dist/               # Built production files
│   ├── package.json
│   └── vite.config.ts
├── tests/                  # Test suite
│   ├── test_analyzer.py
│   ├── test_storage.py
│   └── test_integration.py
├── config.py               # Centralized configuration
├── exceptions.py           # Custom exceptions
├── logger.py               # Structured logging
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## 🎯 Quick Start (5 Minutes)

### Prerequisites
- Python 3.11+
- Node.js 18+
- AWS Builder ID (free from AWS)
- Git

### Installation

```bash
# 1. Clone and enter directory
git clone <your-repo>
cd janus-clew

# 2. Set up Python environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure AWS
cp .env.example .env
# Edit .env and add your AWS_BUILDER_ID_EMAIL

# 4. Set up frontend (already built, but you can rebuild)
cd frontend
npm install --legacy-peer-deps
# Frontend is already built in frontend/dist/
```

### Run Everything

```bash
# Terminal 1: Start backend API (port 3000)
python -m backend

# Terminal 2: (optional) Start frontend dev server (port 5173)
cd frontend
npm run dev

# Terminal 3: Analyze your repositories
janus-clew analyze ~/Your-Honor ~/Ariadne-Clew ~/TicketGlass

# Open http://localhost:3000 or http://localhost:5173
```

---

## 🎮 Using the Dashboard

### 1. View Timeline
- See your complexity progression across projects
- Line chart shows growth trajectory
- Click on projects for details

### 2. Explore Skills
- Discover technologies you've learned
- View confidence levels for each skill
- See which projects use which technologies

### 3. Analyze Growth
- Overall growth metrics
- Project comparison
- Detailed breakdown table

### 4. Share Your Growth
- Download as HTML for sharing
- Copy to clipboard for presentations
- Perfect for LinkedIn, portfolios, interviews

---

## 🔧 CLI Commands

```bash
# Analyze repositories
janus-clew analyze ~/repo1 ~/repo2 ~/repo3

# Check status
janus-clew status

# View demo
janus-clew demo

# Verbose output
janus-clew -v analyze ~/repo
```

---

## 🌐 API Endpoints

### Health & Status
```
GET  /api/health                    # Health check
GET  /api/status                    # Alias for health
```

### Analyses
```
GET  /api/analyses                  # All analyses
GET  /api/analyses/latest           # Most recent
GET  /api/timeline                  # Timeline data
GET  /api/skills                    # Detected skills
GET  /api/growth                    # Growth metrics
GET  /api/complexity/{project}      # Complexity breakdown
```

### Swagger Docs
```
http://localhost:3000/docs          # Interactive API docs
http://localhost:3000/redoc         # ReDoc API docs
```

---

## 🎨 Features

### Timeline Visualization
- Line chart showing complexity growth
- Project-by-project breakdown
- Commit counts per project
- Technology stacks displayed

### Skills Detection
- Automatic technology extraction
- Confidence scoring
- Project mapping
- Unique skill tracking

### Growth Metrics
- Overall complexity trends
- Growth rate calculation
- Total commits tracked
- Project comparison

### Export & Share
- Beautiful HTML export
- Shareable cards
- Presentations ready
- LinkedIn/Portfolio friendly

### Dark Mode
- Toggle in navbar
- Persisted preference
- System preference detection
- Comfortable for all lighting

---

## 🚨 Data Storage

All analysis data is stored locally in:
```
~/.janus-clew/analyses/
```

Each analysis is a timestamped JSON file with structure:
```json
{
  "timestamp": "2025-11-08_10-30-00",
  "projects": [...],
  "overall": {...},
  "patterns": null,
  "recommendations": null
}
```

### Clean Up
```bash
# Remove all analyses
rm -rf ~/.janus-clew/analyses/*

# View all analyses
ls ~/.janus-clew/analyses/
```

---

## 🧪 Testing

### Run Tests
```bash
pytest tests/ -v                    # All tests
pytest tests/test_analyzer.py -v   # Specific test
pytest --cov                        # With coverage
```

### Expected Output
```
========================= test session starts ==========================
tests/test_analyzer.py::TestAnalysisEngine::test_calculate_complexity PASSED
tests/test_storage.py::TestStorageManager::test_save_analysis PASSED
========================= X passed in X.XXs ==========================
```

---

## 🔧 Configuration

Edit `.env` file:

```bash
# AWS
AWS_REGION=us-west-2
AWS_BUILDER_ID_EMAIL=your@email.com

# Environment
JANUS_ENV=development
JANUS_VERBOSE=true

# Server
API_HOST=127.0.0.1
API_PORT=3000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Amazon Q
AMAZON_Q_TIMEOUT=60
AMAZON_Q_RETRIES=3
AMAZON_Q_BACKOFF=2.0

# Logging
LOG_LEVEL=DEBUG
```

---

## 📊 How It Works

### Architecture Flow
```
CLI Tool
  ↓
Repository Analysis (Git Parsing + AST)
  ↓
Complexity Scoring (Multi-factor algorithm)
  ↓
Amazon Q Analysis (Natural language insights)
  ↓
Local Storage (~/.janus-clew/)
  ↓
FastAPI Server (REST API)
  ↓
React Dashboard (Beautiful visualization)
```

### Complexity Calculation
```
Total Score = Files (0-3) + Functions (0-4) + Classes (0-2) + Nesting (0-1)
             = multi-factor analysis, harder to game than simple formula
```

### Skill Detection
```
Technologies extracted from:
- requirements.txt (Python deps)
- package.json (Node deps)
- Go files (*.go)
- Code imports (detected in AST)
```

---

## 🎯 Use Cases

### Personal Use
- Track your learning progress over time
- See which technologies you're improving at
- Understand your coding journey

### Job Interviews
- Show your growth trajectory
- Demonstrate skill acquisition
- Prove your abilities objectively

### Portfolio
- Add to your website
- Share on LinkedIn
- Include in GitHub README

### Learning Tracking
- Monitor improvement between projects
- Identify skill gaps
- Plan learning goals

---

## 🚀 Phase 2 (Optional - Future)

Coming soon:
- [ ] AgentCore pattern detection
- [ ] Intelligent recommendations
- [ ] Cross-project pattern analysis
- [ ] Career guidance

---

## 🛠️ Development

### Build Frontend
```bash
cd frontend
npm run build      # Production build
npm run dev        # Development with HMR
npm run preview    # Preview production build
```

### Code Formatting
```bash
make format        # Black + isort
make lint          # Check formatting
```

### Development Tools
- **Backend:** FastAPI, Pydantic, SQLAlchemy patterns
- **Frontend:** React 19, TypeScript, Tailwind CSS, Recharts
- **Testing:** pytest, unittest.mock
- **Build:** Vite, TypeScript compiler

---

## 📝 Documentation

### Backend
- `config.py` - Configuration management
- `exceptions.py` - Error handling
- `logger.py` - Logging system
- `cli/analyzer.py` - Analysis engine
- `cli/aws_q_client.py` - Amazon Q integration
- `backend/services.py` - Business logic

### Frontend
- `src/services/api.ts` - API client with mock fallback
- `src/pages/Dashboard.tsx` - Main dashboard
- `src/components/*.tsx` - Reusable components

---

## 🔒 Security Notes

### Local Use Only
This tool is designed for **local development and personal use**.

### Privacy
- All data stored locally (~/.janus-clew/)
- No cloud sync (unless you add it)
- No analytics or tracking
- No data sent to external servers (except Amazon Q)

### Production Use
For production deployment, add:
- Authentication (JWT tokens, AWS IAM)
- HTTPS/TLS
- Rate limiting
- Input validation
- Audit logging

---

## 🤝 Contributing

To contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests for new code
5. Format code: `make format`
6. Submit a pull request

---

## 📄 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

Built for **AWS Global Vibe: AI Coding Hackathon 2025**

**Tools & Technologies:**
- Python 3.11 + FastAPI
- React 19 + TypeScript
- Amazon Q Developer
- Tailwind CSS + Recharts
- GitPython + AST parsing

**Philosophy:**
- Local-first, privacy-focused
- Transparent methodology
- Evidence-backed insights
- No vendor lock-in

---

## 📞 Support

### Common Issues

**Q: "Amazon Q CLI not found"**
A: Install: `pip install amazon-q` or set `JANUS_USE_MOCK=true` to use mock data

**Q: "Port 3000 already in use"**
A: Set `API_PORT=3001` in `.env` and rebuild

**Q: "No analyses found"**
A: Run: `janus-clew analyze ~/your-repo` first

**Q: "Frontend not loading"**
A: Make sure backend is running on port 3000 or update API URL in frontend

### Get Help
- Check `.env` configuration
- Run in verbose mode: `janus-clew -v`
- Check logs in colored output
- Review API docs at http://localhost:3000/docs

---

## 🎉 You're All Set!

You now have a complete, production-ready coding growth tracker.

**Next steps:**
1. ✅ Install dependencies
2. ✅ Configure AWS Builder ID
3. ✅ Analyze your repositories
4. ✅ Open dashboard
5. ✅ Share your growth!

Good luck and enjoy tracking your progress! 🚀

---

**Version:** 0.2.0  
**Last Updated:** November 8, 2025  
**Status:** Complete MVP Ready to Demo

