from transformers import pipeline

# Load summarization model
summarizer = pipeline("text2text-generation", model="t5-small")

text = """
Artificial Intelligence is transforming industries across the world. 
It automates repetitive tasks, improves operational efficiency, and 
enables better decision-making through advanced data analytics. 
AI systems are used in healthcare for diagnosis, in finance for fraud detection, 
and in manufacturing for predictive maintenance. As technology continues to evolve, 
AI is expected to play an even bigger role in innovation and economic growth.
"""

summary = summarizer("summarize: " + text, max_length=50, min_length=10, do_sample=False)

print(summary[0]['generated_text'])