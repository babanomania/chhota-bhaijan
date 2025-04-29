from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

# Load base model
base = AutoModelForCausalLM.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0", device_map="auto")
tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")

# Load LoRA adapter
model = PeftModel.from_pretrained(base, "babanomania/chhota-bhaijaan-lora")

# Move model to correct device
device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
model = model.to(device)


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

# Now you can manually call generate
def chat_with_bhaijaan(prompt: str):
    # Preprocess prompt
    final_prompt = (
        "You are Salman Khan. Reply in first person, confident and short.\n"
        f"Fan: {prompt.strip()}\nSalman:"
    )

    inputs = tokenizer(final_prompt, return_tensors="pt").to(device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=80,
        do_sample=True,
        temperature=0.9,
        top_p=0.95,
        repetition_penalty=1.2,
        pad_token_id=tokenizer.eos_token_id
    )

    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return extract_salman_reply(decoded)

# Example chat
while True:
    user_input = input("\nYou: ")
    if user_input.strip().lower() == "exit":
        break
    reply = chat_with_bhaijaan(user_input)
    print("Bhaijaan:", reply)
