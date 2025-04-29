import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from peft import PeftModel

# Page setup
st.set_page_config(page_title="Chhota Bhaijaan", page_icon="🧢")
st.title("🧢 Chhota Bhaijaan: Your Salman Khan Chatbot")

# Load the base TinyLlama model
base_model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # or your local TinyLlama model
lora_adapter_path = "./models/lora_adapter"

@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        device_map="auto"
    )
    model = PeftModel.from_pretrained(model, lora_adapter_path)
    text_generator = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=200,
        temperature=0.7,
        repetition_penalty=1.1
    )
    return text_generator

def extract_salman_reply(generated_text: str) -> str:
    """
    Extract the first full response line after 'Salman:'.
    Preserves the full line and handles multi-line generations safely.
    """
    lines = generated_text.strip().splitlines()

    for line in lines:
        line = line.strip()
        if line.lower().startswith("salman:"):
            # Return the whole line minus 'Salman:'
            return line[len("Salman:"):].strip()

    # Fallback if "Salman:" wasn't found
    return lines[-1] if lines else "..."


# Load model only once
text_gen = load_model()

# Input form
with st.form(key="query_form"):
    user_input = st.text_input("Ask Bhaijaan anything 👇", placeholder="e.g., Motivate me Salman style!")
    submit_button = st.form_submit_button(label="🎬 Action!")

# Generate answer
if submit_button and user_input:
    with st.spinner("Bhaijaan is thinking... 🎥"):
        prompt = (
            "You are Salman Khan, answering a fan. "
            "Always reply in first person. "
            "Keep it short, confident, emotional — like a Bollywood hero. "
            "Never repeat the user's question. Never repeat lines. "
            "Speak in natural desi style with punch and warmth.\n\n"
            f"Fan: {user_input.strip()}\nSalman:"
        )
        result = text_gen(prompt)
        raw_output = result[0]['generated_text']

        # Display output
        st.success("Here's what Bhaijaan says:")
        print(raw_output)  # Debugging line
        response = extract_salman_reply(raw_output)
        st.write(response)

# Footer with Salman style
st.markdown("""
---
Made with ❤️ and lots of "Being Human" energy!
""")
