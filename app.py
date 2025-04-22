from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
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

class LeafAnalysisResponse(BaseModel):
    disease_detected: str
    confidence: float
    analysis: str
    annotated_image: str  # base64 encoded image

class CropRecommendationResponse(BaseModel):
    recommended_crops: List[str]
    analysis: str

@app.get("/")
def read_root():
    return {"message": "Welcome to GreenHeart.ai API", "endpoints": ["/analyze-leaf", "/recommend-crops"]}

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
        # Clean up temporary file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)

@app.post("/api/v1/recommend-crops", response_model=dict)
async def recommend_crops(sensor_data: SensorData):
    """
    Recommend crops based on sensor data and environmental conditions
    """
    try:
        # Format the sensor data for analysis
        data_array = [
            sensor_data.nitrogen, 
            sensor_data.phosphorus, 
            sensor_data.potassium,
            sensor_data.temperature,
            sensor_data.soil_fertility,
            sensor_data.moisture
        ]
        
        formatted_data = format_sensor_data(data_array)
        
        # Build prompt for crop recommendation
        prompt = f"""
        You are an agricultural expert in India. Based on the following detailed soil and environmental sensor data, recommend crops that are most suitable for cultivation in this region. 
        {formatted_data}
        The season is {sensor_data.season} in India.
        Consider the specific growing conditions in India, and provide a list of crops that will produce high yields with minimal maintenance during the current season. Be certain and specific in your recommendations based on the sensor data provided, and ensure that the crops suggested are well-suited for Indian agriculture.
        Your response should not be ambiguous. Do not say things like 'I am not sure' or 'I cannot be certain'. Instead, provide clear, confident recommendations for the best crops to grow in these conditions.
        """
        
        # Generate crop recommendations
        analysis = generate_crop_recommendation(prompt)
        
        # Extract recommended crops (this is a simplification - would need more parsing)
        # For a real implementation, you might want to parse the analysis to extract a specific list
        recommended_crops = ["Rice", "Wheat", "Cotton"]  # Placeholder
        
        return {
            "recommended_crops": recommended_crops,
            "analysis": analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)