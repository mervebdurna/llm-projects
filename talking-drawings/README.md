# 🖍️ Talking Drawings

An interactive AI tool that analyzes children's drawings and lets you chat about them.  
Powered by OpenAI’s GPT-4o model and built with Gradio.

## What It Does

- 🧒 Upload a child's drawing  
- 🎯 Get an emotional and visual analysis  
- 💬 Ask questions and discuss the interpretation

## How to Use

1. Upload a drawing image (PNG/JPG).
2. Enter the child’s name and age.
3. Click **Analyze Drawing**.
4. After analysis, type a message to chat about the drawing.

## Demo

Try the live demo here:  
🔗 [https://huggingface.co/spaces/mervebd/talking-drawings](https://huggingface.co/spaces/mervebd/talking-drawings)

---

## Development

- Built with Python, Gradio, OpenAI GPT-4o
- Requires `OPENAI_API_KEY` environment variable to run locally

```bash
pip install -r requirements.txt
python app.py
