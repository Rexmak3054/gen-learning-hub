# Grace Papers Gen - AI Learning Platform

An AI-powered learning platform with course generation capabilities.

## 🏗️ Project Structure

```
grace-papers-gen/
├── frontend/              # React.js frontend application
├── backend/               # Full Python FastAPI backend (development)
├── api/                   # Simplified backend for Vercel deployment
├── requirements.txt       # Python dependencies (root level)
├── vercel.json           # Vercel deployment configuration
└── VERCEL_ENV_SETUP.md   # Environment variables guide
```

## 🚀 Quick Deploy to Vercel (5 minutes)

### 1. Initialize Git
```bash
cd grace-papers-gen
chmod +x setup-git.sh
./setup-git.sh
```

### 2. Push to GitHub
```bash
# Create a new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/grace-papers-gen.git
git branch -M main
git push -u origin main
```

### 3. Deploy to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click **"New Project"**
3. Import your GitHub repository
4. Vercel auto-detects the configuration
5. Click **"Deploy"**

✅ **Your app is now live!** (with mock data)

### 4. Add AWS Integration (Optional)
See `VERCEL_ENV_SETUP.md` for detailed instructions on connecting your AWS services.

## 🔧 Local Development

### Backend (Full version)
```bash
cd backend
pip install -r requirements.txt
python main_with_agent.py
```

### Frontend
```bash
cd frontend
npm install
npm start
```

### Simplified Backend (Vercel version)
```bash
cd api
pip install -r requirements.txt
python index.py
```

## 📋 Environment Variables

The app works with mock data by default. To enable real data, add these environment variables in Vercel:

### Required for AWS Integration
- `AWS_ACCESS_KEY_ID` - Your AWS access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret key  
- `AWS_REGION` - Your AWS region (default: ap-southeast-2)
- `DDB_TABLE` - Your DynamoDB table name (default: Courses)
- `OS_ENDPOINT` - Your OpenSearch endpoint URL

### Optional
- `OPENAI_API_KEY` - For AI features
- `CORS_ORIGINS` - Allowed origins for CORS

## 🧪 Testing Your Deployment

### Test Endpoints
```bash
# Health check
curl https://your-app.vercel.app/api/health

# Search courses (works with mock data)
curl -X POST https://your-app.vercel.app/api/search-courses \
  -H "Content-Type: application/json" \
  -d '{"query": "python programming", "k": 5}'

# Check environment (debug)
curl https://your-app.vercel.app/api/debug/env
```

## 📚 API Endpoints

- `GET /api/health` - Health check
- `GET /api/test` - Simple test endpoint
- `POST /api/search-courses` - Search for courses
- `GET /api/user-profile/{user_id}` - Get user profile
- `GET /api/course/{course_id}` - Get course details
- `GET /api/debug/env` - Environment debug info

## 🔄 Development Workflow

1. **Make changes** in your local environment
2. **Test locally** using the backend or api folder
3. **Push to GitHub** - triggers automatic deployment
4. **Test on Vercel** - changes go live automatically

## 🐛 Troubleshooting

### App shows mock data instead of real courses
- Check AWS environment variables in Vercel dashboard
- Verify AWS credentials are valid
- Check logs in Vercel dashboard

### CORS errors
- Add your domain to `CORS_ORIGINS` environment variable
- Or use `*` for testing (not recommended for production)

### Deployment fails
- Check requirements.txt for compatible versions
- Verify vercel.json configuration
- Check Vercel build logs

## 🎯 Next Steps

1. ✅ **Deploy basic version** (you're here!)
2. **Add AWS credentials** for real data
3. **Customize frontend** with your branding
4. **Add authentication** for user management
5. **Scale with advanced features** from the full backend

## 📖 Additional Resources

- `VERCEL_ENV_SETUP.md` - Detailed environment setup guide
- `frontend/README.md` - Frontend-specific documentation
- `backend/README.md` - Full backend documentation
