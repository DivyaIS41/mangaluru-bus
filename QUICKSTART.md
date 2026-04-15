# 🚀 Quick Reference Guide

A one-page reference for common tasks and navigation.

## 📍 You Are Here

Your **Mangaluru Bus Navigator** project is now:
- ✅ Secure (no credentials exposed)
- ✅ Documented (3,500+ lines)
- ✅ Ready for GitHub

## ⚡ Quick Commands

### Setup (First Time)
```bash
cd "d:\Sahyadri\SEM 6 MATERIALS\BIG DATA\PROJECT\mangaluru-bus"
python -m venv venv
venv\Scripts\activate            # Windows
source venv/bin/activate         # macOS/Linux
pip install -r requirements.txt
cp .env.example .env.local       # Edit with your Neo4j credentials
```

### Run Locally
```bash
# Terminal 1: Load data
python dataset/load_graph.py

# Terminal 2: Start Flask
cd Neo4j/backend
python app.py

# Browser: Open http://localhost:5000
```

### Push to GitHub
```bash
git add .
git commit -m "Initial commit: Mangaluru Bus Navigator"
git branch -M main
git remote add origin https://github.com/yourusername/mangaluru-bus.git
git push -u origin main
```

## 📚 Documentation Map

```
START HERE
    ↓
├─ 📖 README.md                    (5 min read)
│  Overview, features, architecture
│
├─ 🛠️ DEVELOPMENT.md               (15 min read)
│  Setup, running locally, debugging
│
├─ 🤝 CONTRIBUTING.md              (10 min read)
│  How to contribute, code standards
│
└─ 🚀 GITHUB_SETUP.md              (20 min process)
   Publishing to GitHub safely
```

## 🎯 By Task

| What I Want | File | Time |
|------------|------|------|
| Understand the project | [README.md](README.md) | 5 min |
| Set up locally | [DEVELOPMENT.md](DEVELOPMENT.md) | 15 min |
| Run the app | [DEVELOPMENT.md#7-run-flask-backend](DEVELOPMENT.md#7-run-flask-backend) | 2 min |
| Modify code | [CONTRIBUTING.md](CONTRIBUTING.md) | 10 min |
| Push to GitHub | [GITHUB_SETUP.md](GITHUB_SETUP.md) | 20 min |
| Use the API | [Neo4j/backend/README.md](Neo4j/backend/README.md#api-endpoints) | 10 min |
| Edit frontend | [frontend/README.md](frontend/README.md) | 10 min |
| Process data | [dataset/README.md](dataset/README.md) | 15 min |
| Something broken? | Find your component's README | 5-15 min |

## 🔐 Security Checklist

Before pushing to GitHub:

```bash
# ✅ Check 1: No .env files in git
git ls-files | grep "\.env"      # Should show nothing

# ✅ Check 2: No hardcoded secrets
git diff --cached | grep -i "password\|api.?key\|token"  # Should show nothing

# ✅ Check 3: Review files to commit
git status

# ✅ Check 4: All checks pass?
# See PREPUSH_CHECKLIST.md for full verification
```

## 📂 File Structure at a Glance

```
mangaluru-bus/
├── README.md                  ← START HERE
├── DEVELOPMENT.md             ← SETUP GUIDE
├── CONTRIBUTING.md            ← CONTRIBUTION RULES
├── GITHUB_SETUP.md            ← HOW TO PUSH
├── PREPUSH_CHECKLIST.md       ← VERIFY BEFORE PUSH
├── DOCUMENTATION_INDEX.md     ← FULL GUIDE
├── PROJECT_SUMMARY.md         ← WHAT WAS DONE
│
├── config.py                  [Shared config]
├── .env.example               [Safe template]
├── .gitignore                 [Enhanced]
├── requirements.txt           [Dependencies]
│
├── data/README.md             [Data guide]
├── dataset/README.md          [Processing guide]
├── Neo4j/backend/README.md    [API docs]
├── frontend/README.md         [UI guide]
│
└── [Python files, HTML, CSV]  [Actual code]
```

## 🔄 Typical Workflow

### Day 1: Initial Setup
```
1. Clone repo
2. Create venv
3. pip install -r requirements.txt
4. cp .env.example .env.local
5. Edit .env.local (Neo4j credentials)
6. python dataset/load_graph.py
7. cd Neo4j/backend && python app.py
8. Open http://localhost:5000
```

### Day 2-N: Development
```
1. git checkout -b feature/my-feature
2. Make changes
3. Test locally
4. git commit -m "description"
5. git push origin feature/my-feature
6. Create PR on GitHub
```

### Deployment: Push to GitHub
```
1. Check PREPUSH_CHECKLIST.md
2. Verify no secrets (run security checks)
3. git add .
4. git commit
5. Follow GITHUB_SETUP.md
6. git push origin main
```

## 🆘 Emergency Guide

**"Something broke after setup"**
1. Check [DEVELOPMENT.md#troubleshooting](DEVELOPMENT.md#troubleshooting)
2. Relevant component README troubleshooting section
3. Search README for error message

**"I accidentally committed secrets"**
1. Read [GITHUB_SETUP.md#if-you-accidentally-pushed-secrets](GITHUB_SETUP.md#if-you-accidentally-pushed-secrets)
2. Follow recovery steps immediately
3. Rotate all credentials

**"I don't know where to start"**
1. Read [README.md](README.md) (5 min)
2. Follow [DEVELOPMENT.md](DEVELOPMENT.md) (15 min)
3. Run locally first before committing

## 📊 Project Stats

| Metric | Value |
|--------|-------|
| Documentation | 3,500+ lines |
| Components | 5 (Data, Backend, Frontend, Config, CI/CD) |
| Python Files | 5 |
| README Files | 9 |
| Security Checks | 4 automated + manual |
| API Endpoints | 4 major |
| Setup Time | ~30 minutes |
| Deployment Ready | ✅ Yes |

## 🎓 Key Concepts

- **Neo4j** - Graph database storing bus routes
- **Flask** - Backend REST API server
- **Leaflet** - Interactive web map
- **Dijkstra** - Pathfinding algorithm
- **CSV** - Data format
- **Environment Variables** - Secure config

## 💾 Important Files

| File | What to Do |
|------|-----------|
| `.env.local` | **Never commit** - Has real credentials |
| `.env.example` | **Safe to commit** - Template only |
| `config.py` | Read-only - Handles env config |
| `requirements.txt` | Update when adding dependencies |
| `.gitignore` | Keep as-is, prevents accidents |

## 🌐 Key URLs

| Resource | URL |
|----------|-----|
| Local App | http://localhost:5000 |
| Neo4j Browser | http://localhost:7474 |
| GitHub Repo | https://github.com/yourusername/mangaluru-bus |
| Documentation | [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) |

## ✅ Pre-Push Checklist (TL;DR)

```
☐ Read PREPUSH_CHECKLIST.md
☐ git ls-files | grep "\.env"  # Nothing should show
☐ git status                   # Only modified files
☐ git diff --cached | grep -i password  # Should be empty
☐ Tested locally - app.py runs fine
☐ All documentation updated
☐ No hardcoded secrets in code
☐ Ready to: git push origin main
```

## 🚀 Next Steps

### Immediate (Now)
1. ✅ You've read this guide
2. ⏭️ Read [README.md](README.md)
3. ⏭️ Follow [DEVELOPMENT.md](DEVELOPMENT.md)

### Short-term (Today)
- [ ] Setup locally
- [ ] Run the application
- [ ] Test the map interface

### Medium-term (This Week)
- [ ] Make improvements/fixes
- [ ] Complete [PREPUSH_CHECKLIST.md](PREPUSH_CHECKLIST.md)
- [ ] Push to GitHub using [GITHUB_SETUP.md](GITHUB_SETUP.md)

### Long-term (Ongoing)
- [ ] Follow [CONTRIBUTING.md](CONTRIBUTING.md) for team
- [ ] Keep documentation updated
- [ ] Maintain security practices

## 🎯 Success Criteria

Your project is ready when:

✅ Can run locally without errors  
✅ All documentation complete  
✅ No `.env.local` in git  
✅ Security checks pass  
✅ API endpoints working  
✅ Frontend renders correctly  
✅ Ready to push to GitHub  

## 📞 Support

- **General questions?** → [README.md](README.md)
- **Setup help?** → [DEVELOPMENT.md](DEVELOPMENT.md)
- **Want to contribute?** → [CONTRIBUTING.md](CONTRIBUTING.md)
- **GitHub help?** → [GITHUB_SETUP.md](GITHUB_SETUP.md)
- **Full index?** → [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)

---

**You are HERE** ✨  
**You are READY** 🚀  
**Go NOW** 💪

[Next: Read README.md](README.md)
