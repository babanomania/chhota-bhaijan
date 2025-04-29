# app.py - Try Chhota Bhaijaan LoRA model
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from peft import PeftModel

print("⏳ Loading Chhota Bhaijaan...")

# Load base model and tokenizer
base_model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
adapter_id = "babanomania/chhota-bhaijaan-lora"

tokenizer = AutoTokenizer.from_pretrained(base_model_id)
base_model = AutoModelForCausalLM.from_pretrained(base_model_id, device_map="auto")
model = PeftModel.from_pretrained(base_model, adapter_id)

generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

print("\n🤖 Ask Bhaijaan something (type 'exit' to quit):")

while True:
    prompt = input("\nYou: ")
    if prompt.strip().lower() == "exit":
        break

    full_prompt = (
        f"You are Salman Khan. Answer in first person. Keep it short, confident, and filmi.\n"
        f"Fan: {prompt.strip()}\nSalman:"
    )

    result = generator(full_prompt, max_new_tokens=80, do_sample=True, temperature=0.9)
    response = result[0]["generated_text"].split("Salman:")[-1].strip()
    print("Bhaijaan:", response)
