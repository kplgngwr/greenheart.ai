import google.generativeai as genai
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

def set_model():
    """Configure the Generative AI model using the Gemini API."""
    genai.configure(api_key=api_key)

    generation_config = {
        "temperature": 0.4,
        "top_p": 1,
        "top_k": 32,
        "max_output_tokens": 4096,
    }

    safety_settings = [
        {"category": f"HARM_CATEGORY_{category}", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
        for category in ["HARASSMENT", "HATE_SPEECH", "SEXUALLY_EXPLICIT", "DANGEROUS_CONTENT"]
    ]

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        safety_settings=safety_settings,
    )
    return model

def read_image_data(file_path):
    image_path = Path(file_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Could not find image: {image_path}")
    return {"mime_type": "image/jpeg", "data": image_path.read_bytes()}

def generate_gemini_response(prompt, image_path, sensor_data=None):
    """Generate a response from the Gemini API based on the prompt and image."""
    model = set_model()
    image_data = read_image_data(image_path)
    if sensor_data is not None:
        prompt += f"\nSensor Data: {sensor_data}"
    response = model.generate_content([prompt, image_data])
    return response.text

def build_prompt():
    """Build the prompt for the generative AI model."""
    return '''
You are GreenHeart AI, an advanced agricultural assistant. Your job is to generate a highly personalized, data-driven crop advisory for Indian farmers based on their land, soil, weather, and market data. Use the following structure and tone:

1. **Personalized Greeting**: Address the farmer directly and mention their location and land details if provided.
2. **Primary Crop Recommendation**: Clearly state the best crop for the current season and explain why, referencing soil, weather, and satellite data.
3. **Soil Suitability**: Analyze soil type, fertility, and structure using available data (e.g., Sentinel-2, ESRI layers).
4. **Water Availability**: Reference rainfall and irrigation data (e.g., CHIRPS, IMD) to advise on water needs and rain-fed potential.
5. **Market Demand**: Use recent Agmarknet/eNAM price trends to justify the crop choice and mention average selling price.
6. **Predicted Yield & Profit**: Estimate yield and net profit using district success rates and NDVI patterns.
7. **Nearby Crop Pattern**: Advise on crop saturation in the region and whether the farmer is making a safe or risky choice.
8. **Alternative Crop Suggestions**: List 1-2 more profitable or resilient alternatives, with profit estimates and suitability notes.
9. **Actionable Recommendations**: Give specific, timely advice (e.g., fertilizer, irrigation schedule, pest alerts) based on local data.
10. **Data Sources**: Mention that the plan is optimized using satellite, weather, crop history, and mandi pricing data.
11. **Ongoing Support**: Reassure the farmer they will receive weekly advisories and smart alerts.

**Tone:** Friendly, clear, and confident. Use emojis and bullet points for readability. Always localize advice to the farmer's region and season. If data is missing, make reasonable assumptions and state them.

If the input is not related to agriculture or is unclear, politely ask for more details.
'''

def generate_crop_recommendation(prompt):
    model = set_model()
    response = model.generate_content(prompt)
    return response.text


