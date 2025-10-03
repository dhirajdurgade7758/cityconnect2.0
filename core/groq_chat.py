
import os
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import google.generativeai as genai

# Configure Gemini client
GEMINI_API_KEY = getattr(settings, "GEMINI_API_KEY", None)
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def ask_gemini(user_message: str):
    """
    Send user query to Gemini and return the response.
    """
    if not GEMINI_API_KEY:
        return "⚠️ Gemini API key not configured."

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")

        # Combine system prompt + user input
        system_prompt = (
            "You are **PuneBot** — a smart, friendly, and knowledgeable AI chatbot specialized in Pune city.\n\n"
            "🎯 Your goal is to assist users by answering questions related to:\n"
            "- Local laws, governance, and municipal services (PMC, PCMC)\n"
            "- Public transport (PMPML, metro, rickshaws)\n"
            "- Civic issues (garbage, road damage, electricity, water supply)\n"
            "- Pune's history, culture, festivals, and local places\n"
            "- Government schemes, helplines, and online portals\n\n"
            "📝 Respond in **Markdown format** using lists, bold, links, and headings to improve clarity.\n\n"
            "✂️ Keep responses **brief, specific, and practical**. Avoid long explanations unless asked.\n"
            "Always assume the user is a Pune citizen looking for useful local help.\n\n"
            "If a question is unclear, briefly ask for clarification before answering."
        )

        # Gemini does not support role-based messages like OpenAI/Groq
        response = model.generate_content(
            f"{system_prompt}\n\nUser: {user_message}\n\nPuneBot:"
        )

        return response.text.strip()

    except Exception as e:
        return f"⚠️ Error: {str(e)}"


@csrf_exempt
def chat_api(request):
    """
    Django API view for Gemini-powered chatbot.
    """
    if request.method == "POST" and request.user.is_authenticated:
        data = request.POST
        user_msg = data.get("message", "")
        reply = ask_gemini(user_msg)
        return JsonResponse({"reply": reply})

    return JsonResponse({"error": "Invalid request"}, status=400)
