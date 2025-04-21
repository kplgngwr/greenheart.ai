# GreenHeart.ai 🌱

An AI-powered agriculture assistant designed to help farmers and gardeners identify plant diseases and recommend optimal crops for their specific conditions.

## Project Overview

GreenHeart.ai is a web application built with Streamlit that offers two key features:

1. **Leaf Disease Analyzer** 🔍 - Upload images of plant leaves to:
   - Detect diseases using computer vision
   - Get detailed analysis reports about identified diseases
   - Receive treatment recommendations and corrective measures
   - View annotated images with disease identification

2. **Crop Recommendation System** 🌾 - Input soil and environmental data to:
   - Receive personalized crop recommendations
   - Get insights on optimal growing conditions
   - Maximize yield based on current conditions
   - Make data-driven planting decisions

## Technology Stack

- **Frontend**: Streamlit
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

4. Run the application:
```bash
streamlit run app.py
```

## Using the Application

### Leaf Disease Analyzer

1. Navigate to "🌿 Leaf Disease Analyzer" in the sidebar
2. Upload an image of a plant leaf
3. Click "Analyze Leaf"
4. View the results:
   - Annotated image showing disease detection
   - Detailed analysis report with disease information
   - Treatment recommendations

### Crop Recommender

1. Navigate to "🌱 Crop Recommender" in the sidebar
2. Enter soil and environmental data:
   - Manually or as an array/list
   - Include information like nitrogen, phosphorus, potassium levels
   - Add temperature, soil fertility, and moisture readings
3. Click "Find Optimal Crops"
4. Review recommended crops suited for your conditions

## Project Structure

```
greenheart.ai/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Project dependencies
├── .env                   # Environment variables
├── assets/                # Images and static files
│   ├── Logo.png
│   ├── thankyou.png
│   └── title-greenheart.png
├── examples/              # Sample images for testing
│   ├── dataset-card.jpg
│   └── test_image.jpg
├── models/                # Machine learning models
│   └── model.pt           # YOLOv8 trained model
└── utils/                 # Utility functions
    ├── __init__.py
    ├── formatting.py      # UI formatting utilities
    ├── inference.py       # Disease detection functions
    └── prompt.py          # AI prompt generation utilities
```

## Contributing

Contributions to improve GreenHeart.ai are welcome! Please feel free to submit a pull request.

## License

[MIT License](LICENSE)

## Acknowledgments

- Plant disease dataset contributors
- The Streamlit and PyTorch communities
- Agricultural experts who provided domain knowledge