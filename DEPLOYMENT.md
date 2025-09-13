# RupeeQ AI Calling Agent - Deployment Guide

## 🚀 GitHub & Vercel Deployment

### 1. GitHub Setup

#### Prepare the repository:
```bash
# Remove virtual environment (it's in .gitignore now)
rm -rf venv/

# Initialize git repository
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: RupeeQ AI Calling Agent"

# Add remote repository (replace with your GitHub repo URL)
git remote add origin https://github.com/YOUR_USERNAME/rupeeq-ai-agent.git

# Push to GitHub
git push -u origin main
```

### 2. Vercel Deployment

#### Option A: Deploy from GitHub (Recommended)
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will auto-detect Python and use the `vercel.json` configuration
5. Click "Deploy"

#### Option B: Deploy via Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# For production deployment
vercel --prod
```

### 3. Environment Variables (Vercel)

In Vercel dashboard, add these environment variables:
```
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your-secret-key-here
```

### 4. Important Notes for Vercel

#### Limitations:
- **No persistent file storage** - Database files are ephemeral
- **No background processes** - TTS might not work on serverless
- **Function timeout** - 10 seconds for hobby plan, 60 seconds for pro

#### Recommended Architecture:
For production, consider:
1. **Database**: Use external database (PostgreSQL, MongoDB Atlas)
2. **File Storage**: Use AWS S3 or similar
3. **TTS**: Use cloud TTS services (Google Cloud, AWS Polly)
4. **WebSockets**: Use Redis for session management

### 5. Local Development

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally
python3 run.py
```

### 6. Project Structure for Deployment

```
rupeeq-ai-agent/
├── .gitignore              # Excludes venv, .db files
├── .vercel/               # Vercel configuration (auto-generated)
├── vercel.json            # Vercel deployment config
├── wsgi.py               # WSGI entry point
├── requirements.txt       # Python dependencies
├── run.py                # Local development runner
├── app.py                # Main Flask application
├── ai_agent/             # AI conversation logic
├── database/             # Database models
├── templates/            # HTML templates
└── README.md             # Project documentation
```

### 7. Database Considerations

#### For Vercel (Serverless):
- SQLite files are reset on each deployment
- Use external database for persistence
- Consider MongoDB Atlas or PostgreSQL

#### For Local Development:
- SQLite works fine
- Database persists between runs

### 8. TTS Considerations

#### Local Development:
- macOS: Uses `say` command (works great)
- Windows: Uses SAPI
- Linux: Uses espeak

#### Vercel Deployment:
- Serverless functions don't support audio hardware
- Consider cloud TTS services for production

### 9. Demo URLs

After deployment:
- **Vercel Demo**: `https://your-project.vercel.app`
- **Dashboard**: `https://your-project.vercel.app/`
- **AI Agent**: `https://your-project.vercel.app/ai-agent`

### 10. Troubleshooting

#### Common Issues:
1. **Import Errors**: Check `requirements.txt` includes all dependencies
2. **Database Errors**: Use external database for production
3. **TTS Issues**: Serverless platforms don't support audio hardware
4. **WebSocket Issues**: Vercel has WebSocket limitations

#### Solutions:
1. Use external services for production features
2. Implement fallbacks for serverless limitations
3. Consider hybrid architecture (frontend on Vercel, backend on other platforms)

---

## 📊 Project Size Optimization

**Before**: 757MB (with venv)
**After**: ~2MB (without venv)

The `.gitignore` file excludes:
- Virtual environment (`venv/`)
- Database files (`*.db`)
- Cache files (`__pycache__/`)
- IDE files (`.vscode/`, `.idea/`)
- OS files (`.DS_Store`)

This makes the repository lightweight and suitable for GitHub and Vercel deployment.
