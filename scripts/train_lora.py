from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from peft import get_peft_model, LoraConfig
from datasets import load_dataset

# Model and tokenizer
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
dataset_path = "data/dataset.jsonl"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")

# LoRA config
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)

# Load dataset
dataset = load_dataset('json', data_files=dataset_path, split='train')

# Preprocessing
def preprocess(examples):
    prompt = examples['instruction'] + "\n" + examples['input']
    target = examples['output']
    full_text = prompt + "\n" + target
    tokenized = tokenizer(full_text, truncation=True, padding="max_length", max_length=512)
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized

dataset = dataset.map(preprocess, remove_columns=dataset.column_names)

# Training setup
training_args = TrainingArguments(
    output_dir="./models/lora_adapter",
    per_device_train_batch_size=2,  # Safer for MacBook RAM
    gradient_accumulation_steps=8,
    num_train_epochs=3,
    learning_rate=2e-4,
    logging_steps=10,
    save_steps=50,
    bf16=False,  # MPS doesn't support this well
    fp16=False,  # No CUDA on Mac
)

# Use correct collator for causal LM
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    data_collator=data_collator,
)

# Train
trainer.train()
model.save_pretrained("./models/lora_adapter")

