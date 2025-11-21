# 🚀 Quick Start with Gemini

## 1. Get API Key (2 minutes)

Visit: **https://makersuite.google.com/app/apikey**

Click **"Create API Key"** and copy it.

---

## 2. Update .env (1 minute)

```bash
# Remove or comment out
# OPENAI_API_KEY=sk-...

# Add this line
GOOGLE_API_KEY=AIzaSy...YOUR_KEY_HERE
```

---

## 3. Restart Backend (1 minute)

### Option A: Docker
```bash
docker-compose restart backend
```

### Option B: Local
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## 4. Test (1 minute)

Open browser: http://localhost:5174

Type: "Find remote software engineering jobs"

If you see a streaming response, **you're done!** ✅

---

## Troubleshooting

### Error: "google_api_key is not set"
👉 Check your `.env` file has `GOOGLE_API_KEY=...`

### Error: "No module named 'langchain_google_genai'"
👉 Run: `pip install -r requirements.txt`

### Error: "Rate limit exceeded"
👉 Free tier limit reached. Upgrade or wait.

---

## Cost Comparison

| Model | Input | Output | Savings |
|-------|-------|--------|---------|
| OpenAI GPT-4o-mini | $0.15/1M | $0.60/1M | - |
| **Gemini Flash** | **$0.075/1M** | **$0.30/1M** | **50%** ✅ |

---

## Need Help?

Read the full guide: `GEMINI_MIGRATION.md`


