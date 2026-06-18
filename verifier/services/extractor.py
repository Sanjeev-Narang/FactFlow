import json
from google import genai
from google.genai import types
from decouple import config
from pydantic import BaseModel


# ── Pydantic schemas for structured JSON responses ──────────────────────────

class ExtractedClaims(BaseModel):
    claims: list[str]  # List of verifiable factual statements


class SingleClaimVerdict(BaseModel):
    claim: str            # Echoes back the original claim string to preserve identity
    verdict: str          # Must be exactly: "Verified", "Inaccurate", or "False"
    confidence_score: float
    explanation: str
    corrected_fact: str   # Empty string when verdict is "Verified"


class BatchVerificationVerdict(BaseModel):
    results: list[SingleClaimVerdict]  # Array of structured claim verdicts


# ── Service 1: Pull verifiable claims out of raw PDF text ───────────────────

class GeminiClaimExtractorService:
    """
    Uses Gemini to scan raw PDF text and isolate every verifiable
    factual claim (stats, dates, figures, named assertions).
    """

    def __init__(self):
        self.client = genai.Client(api_key=config("GEMINI_API_KEY"))
        self.model_name = "gemini-2.5-flash"

    def extract_claims(self, pdf_text: str) -> list[str]:
        """
        Returns a flat list of claim strings found in the PDF text.
        Caps at 40 claims to protect against runaway token/search costs.
        """
        prompt = f"""
You are a precise fact-extraction engine.

Read the document text below and extract every verifiable factual claim.
Focus on:
- Statistics and numerical figures (percentages, counts, revenue numbers)
- Dates and time-based assertions ("X happened in YYYY")
- Named entity facts ("Company X has N employees")
- Scientific or technical statements with measurable values
- Any claim that can be objectively verified against real-world data

Rules:
- Each claim must be a single, self-contained sentence.
- Do NOT include opinions, predictions, or vague statements.
- Do NOT duplicate semantically identical claims.
- Extract a maximum of 40 claims.

Document Text:
\"\"\"
{pdf_text[:15000]}
\"\"\"
        """

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractedClaims,
                temperature=0.1,
            ),
        )

        try:
            data = json.loads(response.text)
            return data.get("claims", [])
        except (json.JSONDecodeError, AttributeError):
            return []


# ── Service 2: Judge all claims in a single batch call ───────────────────────

class GeminiJudgeService:
    """
    Compares an entire batch of extracted claims and their corresponding 
    Tavily search snippets against live web evidence in a single API call.
    """

    def __init__(self):
        self.client = genai.Client(api_key=config("GEMINI_API_KEY"))
        self.model_name = "gemini-2.5-flash"

    def judge_all_claims_batch(self, search_bundles: list[dict]) -> list[dict]:
        """
        Accepts a list of dictionaries containing {"claim": str, "web_context": str}.
        Returns a list of structured dictionaries conforming to BatchVerificationVerdict.
        
        Verdict values: "Verified" | "Inaccurate" | "False"
        - Verified   → claim matches the web evidence
        - Inaccurate → claim is partially wrong or outdated
        - False      → claim directly contradicts the web evidence, or no evidence exists
        """
        # Formats the bundled list of dictionary elements cleanly into the prompt string
        formatted_bundles = json.dumps(search_bundles, indent=2)

        prompt = f"""
You are an expert fact-checker. Your job is to analyze an array of claims alongside 
their respective live web contexts, evaluate each one, and provide a verdict layout.

Verdict definitions:
- "Verified"   : The web context clearly supports the claim.
- "Inaccurate" : The claim contains outdated or partially wrong information.
- "False"      : The claim directly contradicts the web evidence, or no
                 credible evidence supports it at all.

DATA BUNDLES TO EVALUATE:
{formatted_bundles}

Rules:
- In `corrected_fact`, provide the accurate information from the web context if 'Inaccurate' or 'False'.
- Leave `corrected_fact` as an empty string if the verdict is 'Verified'.
- Process and return a verdict structure for every single bundle item provided. Do not skip any item.
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=BatchVerificationVerdict,
                    temperature=0.1,  # Keeps outputs consistent and deterministic
                ),
            )
            
            data = json.loads(response.text)
            return data.get("results", [])

        except Exception as e:
            # Fallback block ensures your pipeline data never crashes if the raw API call exceptions out
            return [
                {
                    "claim": bundle.get("claim", ""),
                    "verdict": "False",
                    "confidence_score": 0.0,
                    "explanation": f"Batch validation infrastructure failure: {str(e)}",
                    "corrected_fact": ""
                } for bundle in search_bundles
            ]
