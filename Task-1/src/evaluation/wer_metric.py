from jiwer import wer

def calculate_wer(reference_text, extracted_text):
    return wer(reference_text, extracted_text)
