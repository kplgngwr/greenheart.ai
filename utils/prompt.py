import google.generativeai as genai
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")


def _base_generation_config():
    return {
        "temperature": 0.4,
        "top_p": 1,
        "top_k": 32,
        "max_output_tokens": 4096,
    }


def _safety_settings():
    return [
        {"category": f"HARM_CATEGORY_{category}", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
        for category in ["HARASSMENT", "HATE_SPEECH", "SEXUALLY_EXPLICIT", "DANGEROUS_CONTENT"]
    ]


def generate_with_fallback(prompt, image_data=None):
    """Try multiple model names and return the first successful generate_content result.

    The Google Generative API may expose different model names per project/quota. This function
    attempts a short, safe list (and an optional override via env var) and surfaces a helpful
    error if none work.
    """
    genai.configure(api_key=api_key)

    # Prioritized candidates; allow override via env var
    env_model = os.getenv("GOOGLE_GEMINI_MODEL")
    candidates = []
    if env_model:
        candidates.append(env_model)
    # Common legacy names (without the API "models/" prefix)
    candidates.extend([
        "gemini-1.5-pro",
        "gemini-1.5",
        "gemini-1.0",
        "gemini-1.5-mini",
        "gemini-1.5-flash",
    ])

    # Add a few modern model names (these include the 'models/' prefix in the API)
    known_prefixed = [
        "models/gemini-2.5-pro",
        "models/gemini-2.5-flash",
        "models/gemini-pro-latest",
        "models/gemini-flash-latest",
        "models/gemini-2.5-flash-image",
    ]

    # We'll attempt both forms (plain and prefixed) for each candidate below.
    candidates.extend(known_prefixed)

    last_exc = None
    for model_name in candidates:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=_base_generation_config(),
                safety_settings=_safety_settings(),
            )

            # Attempt generation using the provided prompt and optional image data.
            # Use a try/except so failures for one model fall through to the next.
            if image_data is not None:
                response = model.generate_content([prompt, image_data])
            else:
                response = model.generate_content(prompt)

            return response
        except Exception as e:
            # Keep the last exception to include in the final error if all candidates fail
            last_exc = e
            continue

    # If we reach here, none of the candidates worked
    raise RuntimeError(
        "No available Gemini model succeeded. Last error: " + (str(last_exc) if last_exc else "unknown")
        + ".\nCall ListModels from the Google Generative API to see available models and supported methods, or set the `GOOGLE_GEMINI_MODEL` env var to a supported model name."
    )

def read_image_data(file_path):
    image_path = Path(file_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Could not find image: {image_path}")
    return {"mime_type": "image/jpeg", "data": image_path.read_bytes()}


def generate_gemini_response(prompt, image_path, sensor_data=None):
    """Generate a response from the Gemini API based on the prompt and image.

    This uses `generate_with_fallback` to avoid hard failures when a particular model
    isn't available in the project/quota.
    """
    image_data = read_image_data(image_path)
    if sensor_data is not None:
        prompt = prompt + f"\nSensor Data: {sensor_data}"

    try:
        response = generate_with_fallback(prompt, image_data=image_data)
        return response.text
    except Exception as e:
        # Re-raise with a clearer message for the API layer to catch and return a 4xx/5xx
        raise RuntimeError(f"Gemini generation failed: {str(e)}") from e

def build_prompt():
    """Build the prompt for the generative AI model."""
    return """
You are a highly skilled plant pathologist specializing in the diagnosis and treatment of plant diseases. Your task is to analyze the provided data, which includes an image of a plant and sensor readings, to identify any diseases, infestations, or other issues. Structure your response as follows:

1. **Disease Identification**: Analyze the provided image and sensor data to detect any diseases, pests, or deficiencies.
2. **Detailed Findings**: Provide in-depth findings on the identified issues, including possible causes and severity.
3. **Recommended Actions**: Suggest effective treatment options, preventive measures, and further actions.
4. **Preventive Measures**: Offer recommendations to prevent recurrence.
5. **Expert Recommendations**: Provide long-term health and disease management strategies.

If the condition is unrecognizable, say "I don't know". If the image is not plant-related, respond with "Please upload a valid plant image."
"""

def build_crop_recommendation_prompt(sensor_data: dict) -> str:
    """
    Build a detailed prompt for Gemini to generate a personalized, structured crop advisory script,
    using all available sensor, environmental, and market data.
    """
    details = "\n".join([f"{k}: {v}" for k, v in sensor_data.items() if v is not None])
    return f'''
You are "GreenHeart AI," an expert agricultural advisor for Indian farmers. When given detailed sensor, environmental, and market data, generate a personalized crop planning advisory in the following script format:

🌿 Sample Output Script: Personalized Crop Advisory (Generated by GreenHeart AI)
Hello Farmer! 👋 Based on the data provided below, here is your smart crop planning advisory for this season:

<Insert a summary of the land area, region, district, irrigation type, and any other location-specific details from the data.>

🌾 Primary Crop Chosen: <Crop Name>
Soil Suitability:
<Brief analysis of soil type, fertility, pH, NDVI/EVI, and suitability for the crop, referencing sensor and satellite data if available.>

Water Availability:
<Analysis of rainfall, groundwater, irrigation type, and water sufficiency for the crop, referencing recent data.>

Market Demand:
<Current market trends, price analysis, and demand for the crop in the region, using market_price_per_quintal and crop_history if available.>

Predicted Yield:
<Estimated yield and profit based on local data, NDVI/EVI, crop history, and historical patterns.>

Nearby Crop Pattern:
<Analysis of what neighboring farms are growing, and whether the chosen crop avoids market saturation or risk.>

💡 Alternative Crop Suggestions (More Profitable Options)
<2-3 alternative crops with brief suitability and profit notes.>

🌱 Recommendations:
<Specific, actionable agronomic tips: fertilizer, irrigation, pest alerts, and timing.>

✅ End with a note that the plan is optimized using all provided data, including satellite, rainfall, crop history, and mandi pricing.

If the sensor data is unrealistic or missing, respond with a clear advisory that the data must be verified and realistic values provided before recommendations can be made. If the season or location is unclear, ask for clarification.

---

Here is the data for this advisory:
{details}
'''

def generate_crop_recommendation(prompt_or_data):
    # If a dict is passed, build the prompt using the new function
    if isinstance(prompt_or_data, dict):
        prompt = build_crop_recommendation_prompt(prompt_or_data)
    else:
        prompt = prompt_or_data

    try:
        response = generate_with_fallback(prompt)
        return response.text
    except Exception as e:
        raise RuntimeError(f"Gemini crop recommendation failed: {e}") from e


