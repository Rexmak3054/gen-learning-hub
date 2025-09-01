# Environment Variables Setup for Vercel

## 🚀 Quick Start (Deploy with Mock Data First)

Your app will work immediately with mock data. Add AWS credentials later for real data.

## 📋 Required Environment Variables

### Core Settings (Optional)
```
VERCEL_ENV=production
CORS_ORIGINS=https://your-domain.com,https://your-app.vercel.app
```

### AWS Configuration (Optional - enables real data)
```
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=ap-southeast-2
DDB_TABLE=Courses
OS_ENDPOINT=https://your-opensearch-domain.ap-southeast-2.es.amazonaws.com
OS_INDEX=courses
```

### OpenAI (Optional - for AI features)
```
OPENAI_API_KEY=sk-...
```

## 🛠️ How to Add Environment Variables in Vercel

### Method 1: Vercel Dashboard
1. Go to [vercel.com](https://vercel.com) → Your Project
2. Click **Settings** tab
3. Click **Environment Variables** in sidebar
4. Add each variable:
   - **Name**: AWS_ACCESS_KEY_ID
   - **Value**: Your actual AWS access key
   - **Environment**: Production, Preview, Development
5. Click **Save**
6. **Redeploy** your app

### Method 2: Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Set environment variables
vercel env add AWS_ACCESS_KEY_ID
vercel env add AWS_SECRET_ACCESS_KEY
vercel env add AWS_REGION
vercel env add DDB_TABLE

# Redeploy
vercel --prod
```

## 🔍 Testing Your Deployment

### Phase 1: Test with Mock Data (No AWS needed)
```bash
curl https://your-app.vercel.app/api/health
curl https://your-app.vercel.app/api/test
curl -X POST https://your-app.vercel.app/api/search-courses \
  -H "Content-Type: application/json" \
  -d '{"query": "python programming", "k": 5}'
```

### Phase 2: Test AWS Integration
After adding AWS environment variables:
```bash
curl https://your-app.vercel.app/api/debug/env
curl https://your-app.vercel.app/api/health
```

Look for:
- `aws_initialized: true`
- `services.dynamodb: true`

## 🔐 AWS Credentials Setup

### Option 1: IAM User (Recommended for development)
1. Go to AWS IAM Console
2. Create new user: `grace-papers-vercel`
3. Attach policies:
   - `AmazonDynamoDBFullAccess`
   - `AmazonOpenSearchServiceFullAccess`
4. Create access key → Copy to Vercel

### Option 2: Existing Credentials
Use your existing AWS access key and secret key from your `.env` file.

## 🐛 Troubleshooting

### App works locally but not on Vercel
- Check environment variables are set in Vercel dashboard
- Verify AWS credentials are valid
- Check deployment logs in Vercel dashboard

### "Mock data" showing instead of real courses
- Check `/api/debug/env` endpoint
- Verify AWS credentials in Vercel
- Check DynamoDB table name matches `DDB_TABLE` env var

### CORS issues
- Set `CORS_ORIGINS` to your frontend domain
- Or use `*` for testing (not recommended for production)

## 🚀 Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Vercel project connected to GitHub repo
- [ ] App deploys successfully (with mock data)
- [ ] Frontend can connect to backend
- [ ] AWS environment variables added to Vercel
- [ ] Real data loading from DynamoDB/OpenSearch
- [ ] CORS configured for your domain

## 📝 Notes

- The app gracefully falls back to mock data if AWS is unavailable
- You can deploy and test immediately, then add AWS later
- All sensitive data is handled via environment variables
- Logs show whether AWS services are connected or using mock data
