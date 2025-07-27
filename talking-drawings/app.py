import base64
from dotenv import load_dotenv
import gradio as gr
import io
import json
from openai import OpenAI
import os
import re

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Global vars to hold last drawinganalysis
chat_history = []
last_step1 = ""
last_step2 = ""
last_step3 = ""

# Convert image to base64 string
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    return base64.b64encode(img_bytes).decode("utf-8")

# Analyze drawing
def analyze_drawing(name, age, image):
    global last_step1, last_step2, last_step3

    if image is None:
        return "Please upload a drawing.", "", ""

    img_b64 = image_to_base64(image)
    img_data_url = f"data:image/png;base64,{img_b64}"

    system_prompt = """You are a professional child drawing analyst.

Your task is to analyze a child's drawing in a clear, structured way.

Respond **only** with a JSON object with exactly these keys:

{
  "step_1": "Detailed description of visual elements in the drawing (colors, shapes, figures, layout).",
  "step_2": "Exactly 3 dominant emotions the child might be expressing, each emotion followed by a relevant emoji, separated by commas. Example: Joy 😊, Sadness 😢, Confusion 😕",
  "step_3": "A warm, friendly, and supportive psychological interpretation in 2 to 4 sentences."
}

Rules:
- Do not include anything outside this JSON object.
- Do not add bullet points, numbering, or extra commentary.
- Do not truncate or omit any step.
- Always maintain a professional but gentle tone.
- Only Step 2 contains emojis.

"""

    user_prompt = f"""A child named {name}, age {age}, created the drawing you will analyze. Please provide your analysis based on the image."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": img_data_url}}
                ]
            }
        ],
        max_tokens=800,
    )

    content = response.choices[0].message.content.strip()

    try:
        analysis = json.loads(content)
        step_1 = analysis.get("step_1", "")
        step_2 = analysis.get("step_2", "")
        step_3 = analysis.get("step_3", "")
    except json.JSONDecodeError:
        return "Could not parse the AI response as JSON.", "", ""

    # Save for future chat use
    last_step1, last_step2, last_step3 = step_1, step_2, step_3

    # Format the emotions from step_2
    emotions = ", ".join([e.strip() for e in step_2.split(",") if e.strip()])

    return last_step3, last_step1, emotions


# Reset chat history on new image
def reset_chat_history():
    global chat_history
    chat_history = []
    return []

# Chat with analysis, no image reupload
def chat_with_drawing(user_msg, image):
    global chat_history, last_step1, last_step2, last_step3

    if not last_step1:
        chat_history.append({"role": "user", "content": user_msg})
        chat_history.append({"role": "assistant", "content": "Please analyze a drawing first."})
        return chat_history, ""

    system_prompt = system_prompt = f"""
You are a friendly, empathetic assistant helping to discuss and understand a child's drawing.

Use the following analysis to answer the user's questions clearly and supportively.

Drawing analysis details:
Step 1 - Visual description: {last_step1}
Step 2 - Emotions expressed by the child: {last_step2}
Step 3 - Psychological interpretation: {last_step3}

Please:
- Respond only based on the information above.
- Keep answers warm, respectful, and easy to understand.
- Do not invent new information or speculate beyond the analysis.
- Avoid repetition and keep responses concise but helpful.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            *chat_history,
            {"role": "user", "content": user_msg}
        ],
        max_tokens=500,
    )

    reply = response.choices[0].message.content

    chat_history.append({"role": "user", "content": user_msg})
    chat_history.append({"role": "assistant", "content": reply})

    return chat_history, ""

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("# 🖼️ Talking Drawings\n_Explore the emotions behind your child's artwork._")

    with gr.Row():
        name = gr.Textbox(label="Child's Name", placeholder="e.g., Alex")
        age = gr.Number(label="Age", value=6, precision=0)

    image = gr.Image(type="pil", label="Upload Drawing")

    analyze_btn = gr.Button("🔍 Analyze Drawing")

    with gr.Row():
        interpretation = gr.Textbox(label="🧠 Interpretation", lines=3)
        description = gr.Textbox(label="👁️ What AI Sees", lines=2)
        emojis = gr.Textbox(label="😊 Detected Emotions")

    analyze_btn.click(analyze_drawing, inputs=[name, age, image], outputs=[interpretation, description, emojis])

    gr.Markdown("### 💬 Chat About the Drawing")
    chatbot = gr.Chatbot(label="Drawing Chat", type="messages")
    msg = gr.Textbox(label="Ask something about the drawing", placeholder="Type and press Enter...")

    image.change(reset_chat_history, inputs=[], outputs=[chatbot])
    msg.submit(chat_with_drawing, inputs=[msg, image], outputs=[chatbot, msg])

demo.launch()
