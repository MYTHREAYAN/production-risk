# Production Delay Risk Prediction Dashboard

An industrial-grade dashboard for predicting production order delays with AI-powered advisory chatbot.

## Features
- **Risk Assessment**: Analyzes multiple orders simultaneously with rule-based logic
- **Risk Levels**: LOW / MEDIUM / HIGH with visual badges and score rings
- **Metrics**: Days left, quantity remaining, production capacity, shortage calculation
- **AI Chatbot**: LLaMA 3.3 70B via Groq API for smart production advice
- **Live Dashboard**: Summary tiles with order counts by risk level

## Risk Logic
| Condition | Risk Level |
|-----------|-----------|
| Can produce ≥ 120% of remaining qty AND ahead of schedule | LOW |
| Can produce ≥ remaining qty | MEDIUM |
| Can produce < remaining qty (shortage exists) | HIGH |

**Example:**
- Qty remaining: 600 pcs
- Capacity/day: 200 pcs
- Days left: 2
- Can produce: 400 pcs
- Shortage: 200 pcs → **HIGH RISK**

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Your Groq API Key
Open `app.py` and replace:
```python
GROQ_API_KEY = "gsk_YourGroqAPIKeyHere"
```
With your actual key from https://console.groq.com

### 3. Run the App
```bash
python app.py
```

### 4. Open in Browser
Navigate to: http://localhost:5000

## Project Structure
```
production-risk-dashboard/
├── app.py              # Flask backend + risk logic + Groq AI
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Full frontend (HTML + CSS + JS)
└── README.md
```

## API Endpoints
- `GET /` — Main dashboard
- `POST /api/analyze` — Analyze orders for risk
- `POST /api/chat` — Chat with AI advisor

## Input Fields
| Field | Description |
|-------|-------------|
| Order ID | Unique identifier |
| Delivery Date | Target delivery date |
| Progress % | Current completion percentage |
| Daily Capacity | Units producible per day |
| Total Quantity | Total order quantity in pieces |
| Past Delays | Historical delays in days (optional) |
