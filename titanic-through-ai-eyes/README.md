# Titanic AI Chat

An interactive AI chatbot that lets you ask questions about the Titanic disaster from the perspective of various personas. Powered by OpenAI’s GPT-3.5-turbo model and built with Gradio.

## Personas

- **Statistician 📊**: Analyzes Titanic survival data with statistics like survival rates and age distributions.
- **Data Scientist 🧑‍💻**: Discusses predictive modeling, feature importance, and survival prediction.
- **Sociologist 👩‍🏫**: Explores social class, gender, and norms affecting survival.
- **Insurance Analyst 💼**: Evaluates passenger risk based on demographic and ticket information.
- **1st Class Passenger 🎩**: A privileged survivor reflecting on the disaster.
- **3rd Class Passenger 🎒**: A lower-class passenger sharing experiences of inequality and survival.

## How to Use

1. Select a persona by clicking one of the buttons.
2. Enter your question in the chat box.
3. Press Enter or click submit to get a response from the selected persona.

## Demo

You can try the live demo here:  
[https://huggingface.co/spaces/mervebd/titanic-ai-chat](https://huggingface.co/spaces/mervebd/titanic-ai-chat)

---

## Development

- Built with Python, Gradio, and OpenAI API.
- Environment variable `OPENAI_API_KEY` is required for OpenAI authentication.
- To run locally:  
  ```bash
  pip install -r requirements.txt
  python app.py
