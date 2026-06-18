import os
import io
from concurrent.futures import ThreadPoolExecutor, as_completed

import pdfplumber

from .extractor import GeminiClaimExtractorService, GeminiJudgeService
from .search_api import TavilySearchService

# ── Constants ────────────────────────────────────────────────────────────────

# Capped at 8 to avoid 429 rate-limit errors from Tavily on large PDFs.
MAX_WORKERS = 8


# ── PDF Text Extraction ──────────────────────────────────────────────────────

class PDFParserService:
    """
    Reads raw PDF bytes from RAM (never from disk) and returns
    the full concatenated text across all pages.
    """

    def extract_text(self, file_bytes: bytes) -> str:
        """
        Accepts raw bytes (as read from the Django InMemoryUploadedFile)
        and returns a single text string.
        """
        text_parts = []

        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text.strip())

        full_text = "\n\n".join(text_parts)

        if not full_text.strip():
            raise ValueError(
                "No readable text could be extracted from the PDF. "
                "The document may be scanned or image-based."
            )

        return full_text


# ── Main Pipeline ────────────────────────────────────────────────────────────

class FactCheckPipeline:
    """
    Orchestrates the batch-optimized fact-checking workflow:
      1. Parse PDF bytes → raw text
      2. Extract verifiable claims via Gemini
      3. Fetch web snippets via Tavily for all claims in parallel
      4. Bundle contexts and send to Gemini Judge in ONE single batch call
      5. Persist results to the database in bulk
    """

    def __init__(self):
        self.parser = PDFParserService()
        self.extractor = GeminiClaimExtractorService()
        self.searcher = TavilySearchService()
        self.judge = GeminiJudgeService()

    # ── Public entry point called by views.py ────────────────────────────────

    def process_document(self, doc_record, file_bytes: bytes) -> None:
        """
        Full batch-optimized pipeline for one uploaded PDF.

        Args:
            doc_record : UploadedDocument model instance (status='processing')
            file_bytes : Raw binary content of the PDF (held in RAM)
        """
        # Lazy import here avoids circular-import issues with Django models
        from verifier.models import FactCheckClaim  # adjust app label if needed

        # Step 1 ── Extract raw text from the PDF bytes
        pdf_text = self.parser.extract_text(file_bytes)

        # Step 2 ── Ask Gemini to identify verifiable claims (Gemini Call #1)
        claims = self.extractor.extract_claims(pdf_text)

        if not claims:
            raise ValueError("No verifiable claims could be identified in this document.")

        # Step 3 ── Fetch Tavily web snippets for all claims concurrently
        web_contexts = self._fetch_snippets_parallel(claims)

        # Step 4 ── Build structured bundles pairing each claim to its web context
        search_bundles = []
        for claim_text, context_data in web_contexts:
            search_bundles.append({
                "claim": claim_text,
                "web_context": context_data
            })

        # Step 5 ── Execute ONE single batch judgment call to Gemini (Gemini Call #2)
        batch_results = self.judge.judge_all_claims_batch(search_bundles)

        # Step 6 ── Persist each final verdict to the database in bulk
        claim_objects = []
        for res in batch_results:
            claim_objects.append(
                FactCheckClaim(
                    document=doc_record,
                    extracted_claim=res.get("claim", ""),
                    verdict=res.get("verdict", "False"),
                    confidence_score=res.get("confidence_score", 0.0),
                    explanation=res.get("explanation", ""),
                    corrected_fact=res.get("corrected_fact", ""),
                )
            )

        # Bulk insert for efficiency — single DB round-trip
        FactCheckClaim.objects.bulk_create(claim_objects)

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _fetch_snippets_parallel(self, claims: list[str]) -> list[tuple[str, str]]:
        """
        Runs Tavily search for every claim concurrently.
        Preserves order in the returned list.

        Returns:
            List of (claim_text, web_context_string) tuples.
        """
        results = [None] * len(claims)  # pre-allocate to maintain original PDF order

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Map future → original index to place results back in exact sequence
            future_to_index = {
                executor.submit(self.searcher.fetch_web_snippets, claim): idx
                for idx, claim in enumerate(claims)
            }

            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                claim_text = claims[idx]

                try:
                    web_context = future.result()
                except Exception as exc:
                    # Individual search failure should not crash the document processing
                    web_context = f"Error gathering web search data: {str(exc)}"

                results[idx] = (claim_text, web_context)

        return results
