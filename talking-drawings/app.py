import gradio as gr
from openai import OpenAI
import os
import base64
import io
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Global vars to hold last analysis
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

    system_prompt = """
You are a professional child drawing analyst. Your output must strictly follow the format given by the user.
Do NOT add emojis, numbers, bullet points, or any extra commentary.
Do NOT truncate or cut off any parts.
Only reply with exactly 3 steps labeled as Step 1, Step 2, and Step 3.
"""

    user_prompt = f"""
You are a child drawing analyst. A child named {name}, age {age}, made the drawing you're about to see.

Please respond exactly in this format:

Step 1: Describe in detail the visual elements you observe in the drawing, including colors, figures, and layout.

Step 2: List exactly 3 dominant emotions the child may be expressing. Write only the emotion names separated by commas, no emojis, no extra text, no numbering. Example: Joy, Sadness, Confusion

Step 3: Give a short psychological interpretation (2 to 4 sentences) in a warm, friendly, and supportive tone.

Make sure:
- To label each section exactly as "Step 1:", "Step 2:", and "Step 3:" on separate lines.
- Do not include anything else outside these three steps.
- Do not include emojis anywhere.
- Do not cut off or truncate any step.
"""

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

    content = response.choices[0].message.content

    try:
        step_1 = re.search(r"Step 1:(.*?)(Step 2:|$)", content, re.DOTALL).group(1).strip()
        step_2 = re.search(r"Step 2:(.*?)(Step 3:|$)", content, re.DOTALL).group(1).strip()
        step_3 = re.search(r"Step 3:(.*)", content, re.DOTALL).group(1).strip()
    except Exception:
        return "Could not parse the AI response.", "", ""

    # Save for future chat use
    last_step1, last_step2, last_step3 = step_1, step_2, step_3

    emotions = ", ".join([e.strip() for e in step_2.split(",") if e.strip()])
    return step_3, step_1, emotions

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

    system_prompt = f"""
You're a friendly assistant helping discuss a child's drawing.

Here is the drawing analysis:
Step 1: {last_step1}
Step 2: {last_step2}
Step 3: {last_step3}

Use this information to respond helpfully to the user's questions.
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
