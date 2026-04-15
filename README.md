# SavySoil Backend

A secure FastAPI backend for the SavySoil educational soil fertility simulation. This server handles LLM integration with Google's Gemini API and keeps API keys safe from client-side exposure.

## Architecture

```
GitHub Pages (Frontend)
    ↓ HTTPS POST /review-submission
SavySoil Backend (FastAPI)
    ↓ (with GEMINI_API_KEY in environment)
Google Gemini API
```

The frontend never sees the API key. All LLM communication happens server-to-server with the key stored securely in environment variables.

## Local Development

### Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Create .env File

Copy `.env.example` to `.env` and fill in your actual credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```
GEMINI_API_KEY=your_google_api_key_here
GITHUB_PAGES_ORIGIN=http://localhost:3000  # For local testing
```

Get your API key from: https://aistudio.google.com/app/apikey

### Run Locally

```bash
uvicorn backend.main:app --reload
```

The server will start at `http://localhost:8000`. Visit `/docs` for the interactive Swagger UI.

## API Endpoints

### `GET /health`
Health check. Responds immediately to verify the server is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "SavySoil Backend",
  "gemini_configured": true
}
```

### `POST /review-submission`
Main endpoint. Accepts a student's fertilizer plan and returns Gemini's agronomic feedback.

**Request Body:**
```json
{
  "crop": "wheat",
  "soil_type": "cropping_loam",
  "yield_score": 75,
  "cost_score": 85,
  "fertilizer_plan": [
    {
      "product_name": "Urea",
      "rate_kg_ha": 150,
      "timing": "Sowing"
    },
    {
      "product_name": "Triple Superphosphate",
      "rate_kg_ha": 100,
      "timing": "Sowing"
    }
  ]
}
```

**Response:**
```json
{
  "review": "Well-chosen plan. Your N timing at sowing is appropriate for wheat, and the P placement is good for early vigour. However, consider adding S (e.g., ammonium sulfate) to address the sulfur gap visible in this soil type. Strong overall cost efficiency.",
  "tokens_used": null
}
```

## Deployment (Render)

### Step 1: Push Backend to GitHub

Create a new repository for the backend code:

```bash
cd backend
git init
git add .
git commit -m "Initial SavySoil backend"
git remote add origin https://github.com/YOUR_USERNAME/SavySoil-Backend.git
git branch -M main
git push -u origin main
```

### Step 2: Create Render Web Service

1. Go to [render.com](https://render.com) and sign in
2. Click "New +" → "Web Service"
3. Select your `SavySoil-Backend` repository
4. **Name:** `savysoil-backend` (or similar)
5. **Environment:** Python 3
6. **Build Command:** `pip install -r requirements.txt`
7. **Start Command:** `uvicorn backend.main:app --host 0.0.0.0`

### Step 3: Add Environment Variables

In the Render dashboard, go to **Environment** and add:

| Key | Value |
|-----|-------|
| `GEMINI_API_KEY` | Your API key from https://aistudio.google.com/app/apikey |
| `GITHUB_PAGES_ORIGIN` | `https://YOUR_USERNAME.github.io` |

**Note:** Do NOT include these in your GitHub repository. Render pulls them from the environment dashboard.

### Step 4: Deploy

Render will automatically deploy when you push to `main`. Your backend URL will be something like:
```
https://savysoil-backend.onrender.com
```

Test it:
```bash
curl https://savysoil-backend.onrender.com/health
```

### Step 5: Update Frontend

In your GitHub Pages `script.js`, update the backend URL:

```javascript
const backendUrl = "https://savysoil-backend.onrender.com/review-submission";
```

## Google Gemini API Setup

This backend uses Google's Gemini API for agronomic feedback.

### Getting Your API Key

1. Go to [Google AI Studio](https://aistudio.google.com)
2. Click **"Get API Key"** or go directly to https://aistudio.google.com/app/apikey
3. Click **"Create API Key"**
4. Select **"Create API Key in new project"**
5. Copy your key
6. **Never share or commit this key to GitHub**

### Local Development

Add to `.env`:
```
GEMINI_API_KEY=your_key_here
GITHUB_PAGES_ORIGIN=http://localhost:3000
```

### Production (Render)

Set in Render dashboard environment:
- `GEMINI_API_KEY`: Your Google API key

## CORS Configuration

The backend restricts requests to your GitHub Pages frontend:

```python
allow_origins=["https://gtalckmin.github.io"]
```

For local testing, use `http://localhost:3000`.

## Security Checklist

- [ ] `.env` is in `.gitignore`
- [ ] API key is set as an environment variable on Render, not hardcoded
- [ ] CORS is configured for your specific GitHub Pages domain
- [ ] No secrets are logged or printed to stdout
- [ ] HTTPS is enforced (Render handles this automatically)
- [ ] Backend validates all incoming data with Pydantic models

## Troubleshooting

### 502 Bad Gateway
- Check that `GEMINI_API_KEY` is set correctly in Render environment
- Verify your API key is valid at https://aistudio.google.com/app/apikey
- Check Render logs for more details

### API Key Error
- Make sure your key starts correctly (Google Gemini keys have a specific format)
- Verify you copied the entire key with no spaces
- Regenerate a new key if unsure

### CORS Error in Browser
- Verify your GitHub Pages URL matches `GITHUB_PAGES_ORIGIN` exactly
- Check that the frontend is making a POST request to the correct backend URL

### Timeout
- LLM responses can take 10-30 seconds (this is normal)
- The frontend should display a loading indicator while waiting

## Development Notes

- Pydantic models (`FertilizerPlanItem`, `SavySoilSubmission`) validate all inputs
- Temperature is set to `0.3` for consistent agronomic feedback (not creative responses)
- Responses are limited to `max_output_tokens: 500` to keep feedback concise
- Uses Google's `google-generativeai` SDK for direct integration
- Streaming response collection for real-time feedback

## License

Part of the SavySoil educational project.
