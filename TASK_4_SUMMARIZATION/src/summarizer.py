from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class DocumentSummarizer:
    def __init__(self):
        print("Loading AI Model weights... Please wait.")
        self.model_name = "sshleifer/distilbart-cnn-12-6"
        # Load the "translator" (tokenizer) and the "brain" (model) directly
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)

    def summarize(self, text):
        # Prepare the text for the model
        inputs = self.tokenizer(text[:3000], return_tensors="pt", max_length=1024, truncation=True)
        
        # Generate the summary IDs
        summary_ids = self.model.generate(
            inputs["input_ids"], 
            max_length=150, 
            min_length=40, 
            length_penalty=2.0, 
            num_beams=4, 
            early_stopping=True
        )
        
        # Convert IDs back into human-readable text
        return self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)