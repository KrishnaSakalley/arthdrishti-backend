import os
import httpx
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("KAKUSHIN_API_KEY")
API_URL = os.getenv("KAKUSHIN_API_URL")

# Notice we changed 'prompt: str' to 'messages: list'
async def call_llm(messages: list) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": messages, # Now we send the whole history array directly!
        "temperature": 0.7,
        "max_tokens": 1000
    }

    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(API_URL, json=payload, headers=headers, timeout=30.0)
            res.raise_for_status() 
            
            data = res.json()
            return data["choices"][0]["message"]["content"]
            
        except Exception as e:
            return f"API Error: {str(e)}"

def get_fraud_prompt() -> str:
    try:
        with open("prompts/fraud_prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "{}"

async def check_fraud(offer_details: dict) -> dict:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 5.8: Build a prompt combining user inputs
    user_message = f"""
    Please analyze this loan offer:
    - Loan Amount: ₹{offer_details.get('loan_amount')}
    - Interest Rate: {offer_details.get('interest_rate')}%
    - Processing Fee: {offer_details.get('processing_fee')}%
    - Lender Name: {offer_details.get('lender_name')}
    - Source: {offer_details.get('source')}
    - Description: {offer_details.get('description')}
    """

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": get_fraud_prompt()},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.1, # Extremely low temperature so it sticks strictly to the facts and JSON format
        "max_tokens": 800
    }

    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(API_URL, json=payload, headers=headers, timeout=30.0)
            res.raise_for_status() 
            data = res.json()
            
            ai_reply = data["choices"][0]["message"]["content"]
            
            # 5.10: Clean the response and parse it into structured JSON
            # AI sometimes adds ```json at the start, so we strip it out
            clean_reply = ai_reply.replace("```json", "").replace("```", "").strip()
            
            return json.loads(clean_reply)
            
        except json.JSONDecodeError:
            return {"error": "AI did not return valid JSON", "raw": ai_reply}
        except Exception as e:
            return {"error": f"API Error: {str(e)}"}

# Quant prompt
def get_quant_prompt() -> str:
    try:
        with open("prompts/quant_prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "You are a factual market analyst."

async def analyze_quant(user_message: str, data: dict) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 7.5: Build the prompt combining the user's message and our hardcoded data
    combined_message = f"""
    User's Request: "{user_message}"
    
    HARDCODED DATA TO ANALYZE:
    - Index: {data['name']}
    - Current Level: {data['current_level']}
    - 52W High/Low: {data['52_week_high']} / {data['52_week_low']}
    - PE Ratio: {data['pe_ratio']}
    - 1Y Return: {data['1_year_return']}
    - 3Y Return: {data['3_year_return']}
    - 5Y Return: {data['5_year_return']}
    - 10Y Return: {data['10_year_return']}
    """

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": get_quant_prompt()},
            {"role": "user", "content": combined_message}
        ],
        "temperature": 0.2, # Low temperature to prevent hallucinations
        "max_tokens": 800
    }

    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(API_URL, json=payload, headers=headers, timeout=30.0)
            res.raise_for_status() 
            response_data = res.json()
            return response_data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"API Error: {str(e)}"