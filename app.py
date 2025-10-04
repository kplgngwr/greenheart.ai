from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from typing import List, Union, Optional
import numpy as np
import uvicorn
import cv2
import os
import io
from PIL import Image
import tempfile
import base64
from dotenv import load_dotenv
import google.generativeai as genai

# Import our utility functions
from utils.inference import inference
from utils.prompt import build_prompt, generate_gemini_response
from utils.sensor import format_sensor_data, generate_crop_recommendation

# Load environment variables
load_dotenv()

# Initialize the FastAPI app
app = FastAPI(
    title="GreenHeart.ai API",
    description="API for Plant Disease Analysis and Crop Recommendations",
    version="1.0.0"
)

# Configure CORS with more explicit settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicitly list allowed methods
    allow_headers=["*"],  # Allows all headers
    expose_headers=["Content-Type", "X-Content-Type-Options"],
    max_age=600,  # Caches preflight requests for 10 minutes
)

# Models for request/response validation
class SensorData(BaseModel):
    nitrogen: int
    phosphorus: int
    potassium: int
    temperature: float
    soil_fertility: str
    moisture: float
    season: str
    ndvi: Optional[float] = None
    evi: Optional[float] = None
    soil_ph: Optional[float] = None
    rainfall_last_30_days: Optional[float] = None
    groundwater_depth: Optional[float] = None
    slope_degree: Optional[float] = None
    market_price_per_quintal: Optional[float] = None
    crop_history: Optional[dict] = None
    region: Optional[str] = None
    district: Optional[str] = None
    irrigation_type: Optional[str] = None
    expected_harvest_days: Optional[int] = None

class LeafAnalysisResponse(BaseModel):
    disease_detected: str
    confidence: float
    analysis: str
    annotated_image: str  # base64 encoded image

@app.get("/")
def read_root():
    return {"message": "Welcome to GreenHeart.ai API", "endpoints": ["/analyze-leaf", "/recommend-crops"]}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/v1/analyze-leaf", response_model=dict)
async def analyze_leaf(file: UploadFile = File(...)):
    """
    Analyze a leaf image for diseases and provide recommendations
    """
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Only JPEG and PNG images are supported")
    
    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        tmp_file.write(await file.read())
        tmp_file_path = tmp_file.name
    
    try:
        # Run disease detection model
        model_path = "models/model.pt"
        annotated_image = inference(model_path, tmp_file_path)
        annotated_image_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
        
        # Convert annotated image to base64 for response
        _, buffer = cv2.imencode('.jpg', annotated_image_rgb)
        annotated_image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Generate analysis with Gemini
        prompt = build_prompt()
        analysis_text = generate_gemini_response(prompt, tmp_file_path)
        
        # Extract disease name and confidence (simplified - would need to be parsed from model output)
        # For now using placeholder values
        disease_name = "Detection results in annotated image"
        confidence = 0.95  # This should be extracted from your model's output
        
        return {
            "disease_detected": disease_name,
            "confidence": confidence,
            "analysis": analysis_text,
            "annotated_image": annotated_image_base64
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during analysis: {str(e)}")
    finally:
        # Ensure temporary file is removed
        try:
            if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
        except Exception:
            pass


@app.get("/api/v1/models")
def list_generative_models():
    """List available Google Generative AI (Gemini) models for this API key/project.

    Returns a small JSON list with model names and (if available) supported methods.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="GOOGLE_API_KEY environment variable is not set")

    try:
        genai.configure(api_key=api_key)

        # Try the common list method. Different library versions expose different helpers.
        if hasattr(genai, "list_models"):
            raw = genai.list_models()
        elif hasattr(genai, "Models") and hasattr(genai.Models, "list"):
            raw = genai.Models.list()
        else:
            # Try accessing a client attribute as a last resort
            raw = None

        models_list = []
        if raw is None:
            raise RuntimeError("ListModels method not found in installed google-generativeai package")

        # Normalize different return shapes
        if isinstance(raw, dict):
            candidates = raw.get("models") or raw.get("model") or raw.get("items") or []
        else:
            candidates = raw

        for m in candidates:
            try:
                name = getattr(m, "name", None) or getattr(m, "id", None) or str(m)
                supported = getattr(m, "supported_methods", None) or getattr(m, "supportedMethods", None)
                models_list.append({"name": name, "supported_methods": supported})
            except Exception:
                models_list.append({"raw": str(m)})

        return {"models": models_list}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not list models: {e}")

@app.post("/api/v1/recommend-crops", response_model=dict)
async def recommend_crops(sensor_data: SensorData):
    """
    Recommend crops based on sensor data and environmental conditions
    """
    try:
        data_dict = sensor_data.dict()
        # Build the prompt using the prompt builder
        from utils.prompt import build_crop_recommendation_prompt, generate_crop_recommendation
        prompt = build_crop_recommendation_prompt(data_dict)
        # Generate crop recommendations using Gemini (no image required)
        analysis = generate_crop_recommendation(prompt)
        return {
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.get("/favicon.ico")
async def get_favicon():
    """Return an empty response for favicon requests"""
    return Response(content=b"", media_type="image/x-icon")

if __name__ == "__main__":
    # Ensure uvicorn is only imported when running the module directly
    import uvicorn

    # Start the app defined in this file
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)