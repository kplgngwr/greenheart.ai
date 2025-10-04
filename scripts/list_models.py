#!/usr/bin/env python
"""List available Google Generative AI models for the configured API key.

This script reads `GOOGLE_API_KEY` from the project's .env (via python-dotenv)
and attempts to call the library's list method(s). It prints a JSON array of
objects with `name` and `supported_methods` where available.

Run with the project's venv Python:
  .\greenheart\Scripts\python.exe scripts\list_models.py
"""
import os
import json
import sys
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print(json.dumps({"error": "GOOGLE_API_KEY not set in environment/.env"}))
    sys.exit(1)

try:
    import google.generativeai as genai
except Exception as e:
    print(json.dumps({"error": f"Could not import google.generativeai: {e}"}))
    sys.exit(1)

try:
    genai.configure(api_key=api_key)

    raw = None
    if hasattr(genai, "list_models"):
        raw = genai.list_models()
    elif hasattr(genai, "Models") and hasattr(genai.Models, "list"):
        raw = genai.Models.list()
    else:
        # Try to access a client-style attribute if present
        raw = None

    if raw is None:
        print(json.dumps({"error": "ListModels method not found in installed google-generativeai package"}))
        sys.exit(1)

    # Normalize
    if isinstance(raw, dict):
        candidates = raw.get("models") or raw.get("model") or raw.get("items") or []
    else:
        candidates = raw

    out = []
    for m in candidates:
        try:
            name = getattr(m, "name", None) or getattr(m, "id", None) or str(m)
            supported = getattr(m, "supported_methods", None) or getattr(m, "supportedMethods", None)
            out.append({"name": name, "supported_methods": supported})
        except Exception:
            out.append({"raw": str(m)})

    print(json.dumps({"models": out}, indent=2))
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)
