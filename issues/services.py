import os
import base64
import re
import google.generativeai as genai
from django.conf import settings
from huggingface_hub import InferenceClient
# Configure Gemini client
if getattr(settings, "GEMINI_API_KEY", None):
    genai.configure(api_key=settings.GEMINI_API_KEY)


def verify_issue_image_gemini(image_path, prompt):
    """
    Uses Google Gemini Vision API to verify if the image matches the given prompt.
    Returns dict: {is_verified, score, details} or {error}.
    """
    if not getattr(settings, "GEMINI_API_KEY", None):
        return {"error": "No Gemini API key set"}

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        # Gemini can take raw image bytes
        response = model.generate_content([
            f"Question: {prompt}. Respond with only 'Yes' or 'No' and a brief explanation.",
            {"mime_type": "image/jpeg", "data": image_bytes}
        ])

        result_text = response.text.strip()

        is_verified = "yes" in result_text.lower()
        score = 0.9 if is_verified else 0.1

        return {
            "is_verified": is_verified,
            "score": score,
            "details": result_text
        }

    except Exception as e:
        return {"error": str(e)}


def verify_task_image_gemini(image_path, prompt):
    """
    Uses Google Gemini Vision API to verify if the image matches the given prompt.
    Also estimates EcoCoins to award (30–100) based on task impact.
    Returns dict: {is_verified, score, details, eco_coins} or {error}.
    """
    if not getattr(settings, "GEMINI_API_KEY", None):
        return {"error": "No Gemini API key set"}

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        response = model.generate_content([
            (
                f"Task verification request.\n"
                f"Title & Description: {prompt}\n"
                "1. Respond whether the image matches the description with Yes/No.\n"
                "2. Provide a short explanation.\n"
                "3. Based on task type, location impact, and visible effort, "
                "suggest an EcoCoin award between 30 and 100."
            ),
            {"mime_type": "image/jpeg", "data": image_bytes}
        ])

        result_text = response.text.strip().lower()

        is_verified = "yes" in result_text
        score = 0.9 if is_verified else 0.1

        # Extract EcoCoins (default 30 if not found)
        coins_match = re.search(r'(\d{2,3})', result_text)
        eco_coins = int(coins_match.group(1)) if coins_match else 30
        eco_coins = max(30, min(eco_coins, 100))  # clamp between 30–100

        return {
            "is_verified": is_verified,
            "score": score,
            "details": response.text.strip(),
            "eco_coins": eco_coins
        }

    except Exception as e:
        return {"error": str(e)}



def verify_issue_image_huggingface(image_path, text_query):
    """
    Uses Hugging Face CLIP model to compare image and text_query.
    Returns dict: {is_verified, score, details} or {error}.
    """
    if not getattr(settings, "HF_API_KEY", None):
        return {"error": "No Hugging Face API key set"}

    try:
        hf_client = InferenceClient(token=settings.HF_API_KEY)
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        score = hf_client.image_text_similarity(images=image_bytes, text=text_query)[0]["score"]

        is_verified = score > 0.25  # adjustable threshold
        return {
            "is_verified": is_verified,
            "score": float(score),
            "details": f"Similarity between image and '{text_query}': {score:.2f}"
        }

    except Exception as e:
        return {"error": str(e)}