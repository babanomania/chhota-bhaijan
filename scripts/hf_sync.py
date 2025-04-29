from peft import PeftModel
from transformers import AutoModelForCausalLM

base_model = AutoModelForCausalLM.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
model = PeftModel.from_pretrained(base_model, "./models/lora_adapter")

# Push to Hugging Face
model.push_to_hub("babanomania/chhota-bhaijaan-lora")
