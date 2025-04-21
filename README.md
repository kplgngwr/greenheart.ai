# GreenHeart.ai 🌱

An AI-powered agriculture assistant API that helps farmers and gardeners identify plant diseases and recommend optimal crops for their specific conditions.

## Project Overview

GreenHeart.ai offers two key features available as RESTful API endpoints:

1. **Leaf Disease Analyzer** 🔍 - Upload images of plant leaves to:
   - Detect diseases using computer vision with YOLOv8
   - Get detailed analysis reports about identified diseases
   - Receive treatment recommendations and corrective measures
   - View annotated images with disease identification

2. **Crop Recommendation System** 🌾 - Input soil and environmental data to:
   - Receive personalized crop recommendations optimized for Indian agriculture
   - Get insights on optimal growing conditions
   - Maximize yield based on current conditions
   - Make data-driven planting decisions based on season and local conditions

## Technology Stack

- **API**: FastAPI
- **Computer Vision**: OpenCV, Ultralytics YOLOv8
- **ML/AI**: PyTorch, Google Generative AI (Gemini)
- **Data Processing**: NumPy, Pandas
- **Image Processing**: PIL, OpenCV

## Installation

### Prerequisites

- Python 3.10+
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/kplgngwr/greenheart.ai.git
cd greenheart.ai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Google Generative AI API:
   - Create a `.env` file in the project root
   - Add your Google API key: `GOOGLE_API_KEY=your_api_key_here`

4. Run the API server:
```bash
uvicorn api:app --reload
```

## API Endpoints

### Leaf Disease Analysis
```
POST /api/v1/analyze-leaf
Content-Type: multipart/form-data
{
  "file": [binary image data]
}
```

Response:
```json
{
  "disease_detected": "Leaf Rust",
  "confidence": 0.95,
  "analysis": "The leaf shows signs of...",
  "annotated_image": "[base64 encoded image]"
}
```

### Crop Recommendation
```
POST /api/v1/recommend-crops
Content-Type: application/json
{
  "nitrogen": 50,
  "phosphorus": 50,
  "potassium": 50,
  "temperature": 25.0,
  "soil_fertility": "Medium",
  "moisture": 60.0,
  "season": "summer"
}
```

Response:
```json
{
  "recommended_crops": ["Rice", "Wheat", "Cotton"],
  "analysis": "Based on your soil conditions..."
}
```

## API Documentation

When the API server is running, visit:
- Interactive API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc

## Project Structure

```
greenheart.ai/
├── api.py                 # FastAPI application
├── requirements.txt       # Project dependencies
├── .env                   # Environment variables
├── examples/              # Sample images for testing
│   ├── dataset-card.jpg
│   └── test_image.jpg
├── models/                # Machine learning models
│   └── model.pt           # YOLOv8 trained model
└── utils/                 # Utility functions
    ├── __init__.py
    ├── formatting.py      # API formatting utilities
    ├── inference.py       # Disease detection functions
    ├── prompt.py          # AI prompt generation utilities
    └── sensor.py          # Sensor data processing functions
```

## Integrating with UIs

This API is designed to be easily integrated with any UI platform:

1. **Web Applications**: Use fetch or axios to make API calls from JavaScript
2. **Mobile Apps**: Make HTTP requests from your iOS/Android app
3. **Desktop Applications**: Integrate via HTTP client libraries
4. **IoT Devices**: Connect sensors directly to the API for real-time analysis

## Contributing

Contributions to improve GreenHeart.ai are welcome! Please feel free to submit a pull request.

## License

[MIT License](LICENSE)

## Acknowledgments

- Plant disease dataset contributors
- The PyTorch and FastAPI communities
- Agricultural experts who provided domain knowledge