from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

print("Loading model... Please wait...")

model_name = "google/flan-t5-base"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

with open("input/document.txt", "r", encoding="utf-8") as file:
    text = file.read()

input_text = "Please provide a clear and concise summary of the following text:\n\n" + text

inputs = tokenizer(input_text, return_tensors="pt", truncation=True)

print("Generating summary...")

outputs = model.generate(
    **inputs,
    max_length=120,
    min_length=40,
    num_beams=4,
    early_stopping=True
)

summary = tokenizer.decode(outputs[0], skip_special_tokens=True)

with open("output/summary.txt", "w", encoding="utf-8") as file:
    file.write(summary)

print("Summary saved successfully in output/summary.txt")
