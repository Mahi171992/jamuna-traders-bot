import os
import requests
from fastapi import FastAPI, Request, HTTPException
import google.generativeai as genai

app = FastAPI()

# ================= CONFIGURATION =================
META_TOKEN = os.getenv("META_TOKEN", "EAAPg3fYNYtMBS2uop2eHcDflZAEmaZCzmBSUXnxrZB3ZCcgZAXsPipm2n36B9ZBStbd2FbY4PrmbPGHuEgZBMNXtlDLRqVRFSqeYCfr0ThbZAuWUaR5TZAG0Vrv0ZAxxNchvd6NFE7T7Rf3mXuSwalFTeLGFn9ngoGJMDFh7KhE45twNocRVcEpF0fZCisQ1B0o2AZDZD") 
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "1134604479743949")
WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN", "my_custom_secret_token_123")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AQ.Ab8RN6LL0kTMfqe_t98ZN4kgzb_iFTarLM0bgPWYI5uaUdYOzg")

# জেমিনি এআই কনফিগারেশন
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")


def generate_ai_reply(user_message: str) -> str:
    """কর্পোরেট স্ট্যান্ডার্ডে জেমিনি এআই দিয়ে ডাইনামিক উত্তর তৈরি করা"""
    try:
        # Jamuna Traders-এর প্রফেশনাল কর্পোরেট সিস্টেম প্রম্পট
        prompt = (
            "You are an executive-level corporate AI logistics & customs advisor representing 'Jamuna Traders', "
            "a premiere Customs Clearing & Forwarding (C&F) Agent and Freight Logistics firm in Bangladesh.\n\n"
            "CORPORATE GUIDELINES & PERSONA:\n"
            "1. Tone: Exceptionally polite, professional, formal, and helpful corporate business executive tone.\n"
            "2. Knowledge Base: Import, Export, Air Freight, Sea Freight, Airport Cargo Clearance, Customs SRO, HS Code classification, Tariff estimation, NOC authorizations (e.g., BTRC, DGDA), and documentation support.\n"
            "3. HS Code Requests: If a user asks for an HS Code or customs duty for any product, provide the most relevant 6-to-8 digit HS Code based on WCO/Bangladesh Customs Tariffs, explain the product category clearly, and state that exact duty structures are governed by current NBR SRO notifications.\n"
            "4. Language Handling: Reply in elegant, polished business Bengali if the query is in Bengali, or professional corporate English if in English.\n"
            "5. Structure: Keep responses concise, well-structured, and clear. Avoid overly long disclaimers, but always end with a warm corporate offer to assist further.\n\n"
            f"Client Query: {user_message}"
        )
        response = gemini_model.generate_content(prompt)
        
        if response and response.text:
            return response.text
        else:
            return "ধন্যবাদ Jamuna Traders-এ যোগাযোগ করার জন্য। আপনার অনুসন্ধানের বিস্তারিত উত্তর তৈরি করতে সাময়িক বিলম্ব হচ্ছে। আমাদের সিনিয়র প্রতিনিধি দ্রুতই আপনার সাথে যোগ দেবেন।"

    except Exception as e:
        print(f"Gemini Processing Error: {e}")
        return "ধন্যবাদ Jamuna Traders-এ যোগাযোগ করার জন্য। আমাদের কাস্টমস সার্ভিস টিম অতি শীঘ্রই আপনার সাথে যোগাযোগ করবে।"


def send_whatsapp_message(to_phone: str, text_body: str):
    """মেটা হোয়াটসঅ্যাপ ক্লাউড এপিআই দিয়ে মেসেজ পাঠানো"""
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {META_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "text": {"body": text_body},
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"WhatsApp API Status: {response.status_code}")
    except Exception as e:
        print(f"WhatsApp API Request Failed: {e}")


@app.get("/")
def home():
    return {"status": "Jamuna Traders AI System is Online 24/7"}


@app.get("/webhook")
async def verify_webhook(request: Request):
    """মেটা ওয়েবহুক ভেরিফিকেশন"""
    hub_mode = request.query_params.get("hub.mode")
    hub_verify_token = request.query_params.get("hub.verify_token")
    hub_challenge = request.query_params.get("hub.challenge")

    if hub_mode == "subscribe" and hub_verify_token == WEBHOOK_VERIFY_TOKEN:
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification token mismatch")


@app.post("/webhook")
async def receive_webhook(request: Request):
    """ইনকামিং মেসেজ হ্যান্ডলিং এবং জেমিনি এআই রেসপন্স জেনারেশন"""
    try:
        data = await request.json()
        print(f"Incoming Webhook Data: {data}")

        # হোয়াটসঅ্যাপ মেসেজ ইভেন্ট চেক করা
        if "entry" in data:
            for entry in data["entry"]:
                if "changes" in entry:
                    for change in entry["changes"]:
                        if change.get("field") == "messages":
                            messages = change.get("value", {}).get("messages", [])
                            for message in messages:
                                from_phone = message.get("from")
                                user_message = message.get("text", {}).get("body", "")

                                if user_message:
                                    ai_reply = generate_ai_reply(user_message)
                                    send_whatsapp_message(from_phone, ai_reply)

        return {"status": "success"}
    except Exception as e:
        print(f"Webhook Processing Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")       