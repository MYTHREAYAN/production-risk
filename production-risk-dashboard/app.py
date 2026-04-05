from flask import Flask, render_template, request, jsonify
from datetime import datetime, date
import requests
import json
import os

app = Flask(__name__)

GROQ_API_KEY = "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"  # Replace with your actual Groq API key
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

def calculate_risk(order_id, delivery_date_str, progress_pct, capacity_per_day, total_qty, past_delays=0):
    try:
        delivery_date = datetime.strptime(delivery_date_str, "%Y-%m-%d").date()
    except ValueError:
        return {"error": "Invalid date format"}

    today = date.today()
    days_left = (delivery_date - today).days

    if days_left < 0:
        return {
            "order_id": order_id,
            "risk_level": "HIGH",
            "risk_score": 100,
            "reason": "Delivery date has already passed.",
            "days_left": days_left,
            "can_produce": 0,
            "qty_remaining": total_qty * (1 - progress_pct / 100),
            "progress_pct": progress_pct,
            "capacity_per_day": capacity_per_day,
            "delivery_date": delivery_date_str,
            "past_delays": past_delays
        }

    qty_remaining = total_qty * (1 - progress_pct / 100)
    can_produce = capacity_per_day * days_left
    shortage = qty_remaining - can_produce

    # Risk scoring
    if days_left == 0:
        completion_ratio = 0
    else:
        planned_progress = (1 - (days_left / max((delivery_date - today).days + days_left, 1))) * 100
        completion_ratio = progress_pct / max(planned_progress, 1) if planned_progress > 0 else progress_pct / 100

    delay_penalty = min(past_delays * 5, 20)

    if can_produce >= qty_remaining * 1.2 and completion_ratio >= 1.0:
        risk_level = "LOW"
        risk_score = max(10, 30 - int(completion_ratio * 10) + delay_penalty)
        reason = f"Production is ahead of schedule. Can produce {int(can_produce)} pcs but only {int(qty_remaining)} pcs remain."
    elif can_produce >= qty_remaining:
        risk_level = "MEDIUM"
        risk_score = 50 + delay_penalty
        reason = f"Production is slightly behind. Can produce {int(can_produce)} pcs, needs {int(qty_remaining)} pcs in {days_left} days."
    else:
        risk_level = "HIGH"
        risk_score = min(95, 70 + int((shortage / max(qty_remaining, 1)) * 30) + delay_penalty)
        reason = f"Cannot finish on time! Shortage of {int(shortage)} pcs. Can only produce {int(can_produce)} pcs but {int(qty_remaining)} pcs remain in {days_left} days."

    return {
        "order_id": order_id,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "reason": reason,
        "days_left": days_left,
        "can_produce": int(can_produce),
        "qty_remaining": int(qty_remaining),
        "shortage": int(max(shortage, 0)),
        "progress_pct": progress_pct,
        "capacity_per_day": capacity_per_day,
        "total_qty": total_qty,
        "delivery_date": delivery_date_str,
        "past_delays": past_delays
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.json
    orders = data.get("orders", [])
    results = []
    for order in orders:
        result = calculate_risk(
            order_id=order.get("order_id", "N/A"),
            delivery_date_str=order.get("delivery_date"),
            progress_pct=float(order.get("progress_pct", 0)),
            capacity_per_day=float(order.get("capacity_per_day", 100)),
            total_qty=float(order.get("total_qty", 1000)),
            past_delays=int(order.get("past_delays", 0))
        )
        results.append(result)
    return jsonify({"results": results})


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    dashboard_context = data.get("context", "")
    conversation_history = data.get("history", [])

    system_prompt = f"""You are an expert industrial production planning assistant embedded in a Production Delay Risk Prediction Dashboard. 
You help factory managers understand production risks, delays, and how to mitigate them.

Current Dashboard Data:
{dashboard_context}

Guidelines:
- Be concise and practical
- Give actionable advice
- Use manufacturing/production terminology
- When referencing orders, use their IDs
- Focus on risk mitigation strategies
- Explain the math behind risk calculations when asked
- Be direct and professional
"""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in conversation_history[-10:]:
        messages.append(msg)
    messages.append({"role": "user", "content": user_message})

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.7
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        assistant_message = result["choices"][0]["message"]["content"]
        return jsonify({"reply": assistant_message, "status": "ok"})
    except requests.exceptions.RequestException as e:
        return jsonify({"reply": f"AI service error: {str(e)}. Please check your Groq API key.", "status": "error"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
