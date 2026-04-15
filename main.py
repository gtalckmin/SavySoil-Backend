"""
SavySoil Backend - FastAPI Server with Google Gemini Integration
=================================================================

This FastAPI server receives student fertilizer recommendations from the GitHub Pages frontend,
validates them using Pydantic models, and sends them to Google's Gemini LLM for agronomic review.

The API key is securely stored as an environment variable (never hardcoded).
CORS is configured to allow only the GitHub Pages frontend.

Environment Variables:
  - GEMINI_API_KEY: Your Google Gemini API key (set on hosting platform)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import google.generativeai as genai
import os
from typing import Optional

# ============================================================
# CONFIGURATION
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Your GitHub Pages frontend URL
GITHUB_PAGES_ORIGIN = os.getenv("GITHUB_PAGES_ORIGIN", "https://gtalckmin.github.io")

app = FastAPI(
    title="SavySoil Backend",
    description="Agronomic feedback service for the SavySoil student simulation",
    version="1.0.0"
)

# ============================================================
# CORS MIDDLEWARE
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[GITHUB_PAGES_ORIGIN],
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type"],
)

# ============================================================
# PYDANTIC MODELS (Data Validation)
# ============================================================

class FertilizerPlanItem(BaseModel):
    """Represents a single fertilizer application in the student's plan."""
    product_name: str = Field(..., description="Name of the fertilizer product")
    rate_kg_ha: float = Field(..., ge=0, le=2000, description="Application rate in kg/ha")
    timing: str = Field(..., description="Application timing (Sowing, Emergence, Vegetative)")


class SavySoilSubmission(BaseModel):
    """Complete student submission including crop, soil, and fertilizer plan."""
    crop: str = Field(..., description="Crop type (wheat, canola, lupins)")
    soil_type: str = Field(..., description="Soil type identifier")
    yield_score: int = Field(..., ge=0, le=100, description="Student's calculated yield score")
    cost_score: int = Field(..., ge=0, le=100, description="Student's calculated cost score")
    fertilizer_plan: list[FertilizerPlanItem] = Field(
        default_factory=list,
        description="List of fertilizer applications"
    )


class AdvisoryReviewResponse(BaseModel):
    """Response containing Gemma's agronomic advisory."""
    review: str = Field(..., description="Agronomic feedback from Gemma")
    tokens_used: Optional[int] = Field(None, description="LLM tokens used for response")


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def build_agronomic_prompt(submission: SavySoilSubmission) -> tuple[str, str]:
    """
    Build system and user prompts for Gemma based on the student's submission.
    Returns (system_prompt, user_prompt).
    """
    system_prompt = (
        "You are an expert agronomist evaluating a student's soil fertility and fertilizer plan. "
        "Your role is to provide constructive, educational feedback that helps the student understand "
        "agronomic principles. Review the crop, soil type, and fertilizer choices for:\n"
        "  • Deficiencies or excesses in key nutrients (N, P, K, S, Zn, B, etc.)\n"
        "  • Application timing relative to crop growth stages\n"
        "  • Product selection (e.g., urea vs. ammonium sulfate for dual nutrient needs)\n"
        "  • Cost-effectiveness and sustainability\n"
        "Keep responses concise (5–7 sentences) and educational. Highlight what they did well and "
        "where they can improve."
    )

    plan_summary = "No fertilizers applied" if not submission.fertilizer_plan else "\n".join(
        f"  • {fp.product_name}: {fp.rate_kg_ha} kg/ha at {fp.timing}"
        for fp in submission.fertilizer_plan
    )

    user_prompt = (
        f"Student Submission:\n"
        f"  Crop: {submission.crop}\n"
        f"  Soil Type: {submission.soil_type}\n"
        f"  Yield Score: {submission.yield_score}/100\n"
        f"  Cost Score: {submission.cost_score}/100\n"
        f"  Fertilizer Plan:\n{plan_summary}\n\n"
        f"Please provide agronomic feedback on this student's plan."
    )

    return system_prompt, user_prompt


# ============================================================
# API ENDPOINTS
# ============================================================

@app.get("/health")
async def health_check():
    """
    Health check endpoint. Returns 200 if the server is running.
    Use this to verify the backend is deployed correctly.
    """
    return {
        "status": "healthy",
        "service": "SavySoil Backend",
        "gemini_configured": bool(GEMINI_API_KEY),
    }


@app.post("/review-submission", response_model=AdvisoryReviewResponse)
async def review_submission(submission: SavySoilSubmission):
    """
    Main endpoint: Receive a student's submission and return Gemini's agronomic feedback.
    
    Request body:
      - crop: Crop type (string)
      - soil_type: Soil type identifier (string)
      - yield_score: Calculated yield score (0-100)
      - cost_score: Calculated cost score (0-100)
      - fertilizer_plan: List of {product_name, rate_kg_ha, timing}
    
    Returns:
      - review: Agronomic feedback from Gemini
      - tokens_used: Number of tokens consumed (if provided by LLM)
    """
    
    # Verify API key is configured
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Gemini API key is not configured. Set GEMINI_API_KEY environment variable."
        )

    # Configure Gemini client with the API key
    genai.configure(api_key=GEMINI_API_KEY)

    # Build prompts
    system_prompt, user_prompt = build_agronomic_prompt(submission)

    try:
        # Create client and call Gemini
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Create content for the model
        contents = [
            genai.types.Content(
                role="user",
                parts=[
                    genai.types.Part.from_text(text=f"{system_prompt}\n\n{user_prompt}"),
                ],
            ),
        ]
        
        # Configure generation parameters
        generate_content_config = genai.types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=500,
        )
        
        # Stream and collect response
        review_text = ""
        tokens_used = None
        
        for chunk in client.models.generate_content_stream(
            model="gemini-2.0-flash",
            contents=contents,
            config=generate_content_config,
        ):
            if chunk.text:
                review_text += chunk.text
        
        # If we got an empty response, provide a default
        if not review_text:
            review_text = "Unable to generate feedback. Please try again."
        
        return AdvisoryReviewResponse(review=review_text, tokens_used=tokens_used)
        
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Gemini API error: {str(e)}"
        )


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
async def root():
    """Root endpoint with API documentation."""
    return {
        "service": "SavySoil Backend",
        "version": "1.0.0",
        "docs_url": "/docs",
        "endpoints": {
            "health": "GET /health",
            "review": "POST /review-submission",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
