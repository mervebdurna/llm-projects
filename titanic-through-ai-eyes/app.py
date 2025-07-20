import os
import openai
import gradio as gr
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define personas with their system instructions
personas = {
    "Statistician": "You are a statistician in 1912 analyzing survival data from the Titanic disaster. Speak using survival rates, age distributions, and other descriptive statistics.",
    "Data Scientist": "You are a modern-day data scientist who has trained predictive models on the Titanic dataset. Talk about feature importance, model accuracy, and survival prediction.",
    "Sociologist": "You are a sociologist in 1912 examining the Titanic tragedy to understand how class, gender, and social norms influenced survival outcomes.",
    "Insurance Analyst": "You are an insurance analyst working for a marine insurance company in 1912. Evaluate passenger risk based on age, class, gender, and ticket fare.",
    "1st Class Passenger": "You are an aristocratic 1st class passenger from the Titanic. You survived the disaster and now reflect on the events with pride, privilege, and perhaps bias.",
    "3rd Class Passenger": "You are a 3rd class passenger who experienced the disaster firsthand. You reflect on inequality, survival odds, and how lower-class passengers were treated."
}

def chat_with_persona(persona, message, history):
    """
    Generate a reply from the selected persona using OpenAI's chat completion.
    Maintain conversation history with role and content.
    """
    system_message = personas.get(persona, "You are a helpful assistant.")
    if history is None:
        history = []
    # Build messages with system prompt, conversation history and new user message
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]

    # Call OpenAI chat completion (new API style)
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    assistant_reply = response.choices[0].message.content

    # Update history with user and assistant messages
    history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": assistant_reply}]

    # Return updated history for chatbot display and internal state
    return history, history

def set_persona(persona):
    """
    Update selected persona and reset chat history when persona changes.
    """
    return persona, f"**Current Persona:** {persona}"

with gr.Blocks() as iface:
    gr.Markdown("# Titanic Through AI Eyes")
    gr.Markdown("Ask questions to different personas about the Titanic dataset.")

    chatbot = gr.Chatbot(type="messages")
    msg = gr.Textbox(placeholder="Ask a question...", label="Your Question")
    state = gr.State([])  # Store conversation history

    selected_persona = gr.State("Statistician")  # Default persona
    persona_text = gr.Markdown("**Current Persona:** Statistician")

    with gr.Row():
        # Buttons to switch personas
        btn_stat = gr.Button("Ask Statistician 📊")
        btn_data = gr.Button("Ask Data Scientist 🧑‍💻")
        btn_socio = gr.Button("Ask Sociologist 👩‍🏫")
        btn_ins = gr.Button("Ask Insurance Analyst 💼")
        btn_1st = gr.Button("Ask 1st Class Passenger 🎩")
        btn_3rd = gr.Button("Ask 3rd Class Passenger 🎒")

    # Hidden text elements for button inputs
    persona_stat = gr.Text(value="Statistician", visible=False)
    persona_data = gr.Text(value="Data Scientist", visible=False)
    persona_socio = gr.Text(value="Sociologist", visible=False)
    persona_ins = gr.Text(value="Insurance Analyst", visible=False)
    persona_1st = gr.Text(value="1st Class Passenger", visible=False)
    persona_3rd = gr.Text(value="3rd Class Passenger", visible=False)

    # Connect buttons to change persona and update display text
    btn_stat.click(set_persona, inputs=[persona_stat], outputs=[selected_persona, persona_text])
    btn_data.click(set_persona, inputs=[persona_data], outputs=[selected_persona, persona_text])
    btn_socio.click(set_persona, inputs=[persona_socio], outputs=[selected_persona, persona_text])
    btn_ins.click(set_persona, inputs=[persona_ins], outputs=[selected_persona, persona_text])
    btn_1st.click(set_persona, inputs=[persona_1st], outputs=[selected_persona, persona_text])
    btn_3rd.click(set_persona, inputs=[persona_3rd], outputs=[selected_persona, persona_text])

    # When the user submits a message, run chat_with_persona and update chatbot + state
    # Also clear the input textbox after submit by resetting its value to ""
    msg.submit(chat_with_persona, inputs=[selected_persona, msg, state], outputs=[chatbot, state]).then(
        lambda: "", outputs=msg
    )

iface.launch(server_port=7861)
