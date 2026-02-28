import os
import fitz  # PyMuPDF
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Load your API Key from the .env file
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ ERROR: No API Key found. Check your .env file!")
else:
    genai.configure(api_key=api_key)

def run_summarization_task(pdf_name):
    # Check if the PDF exists
    if not os.path.exists(pdf_name):
        print(f"❌ ERROR: Cannot find '{pdf_name}' in this folder.")
        print(f"Current Folder: {os.getcwd()}")
        return

    print(f"📂 Found {pdf_name}. Extracting text...")
    
    try:
        # Extract text from the PDF
        doc = fitz.open(pdf_name)
        text = "".join([page.get_text() for page in doc])
        
        if not text.strip():
            print("❌ ERROR: The PDF appears to be empty or unreadable.")
            return

        # Connect to the latest available model for 2026
        # Gemini 2.5 Flash is the recommended stable model
        print("🤖 Sending to Gemini AI (Model: gemini-2.5-flash)...")
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"Summarize this documentation with key takeaways and an executive summary:\n\n{text}"
        response = model.generate_content(prompt)
        
        # Display the result
        print("\n" + "="*40)
        print("TASK COMPLETE: GENERATED SUMMARY")
        print("="*40)
        print(response.text)
        
        # Save to a text file for your documentation
        with open("summary_output.txt", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("\n✅ Summary successfully saved to 'summary_output.txt'")

    except Exception as e:
        print(f"❌ AN ERROR OCCURRED: {e}")

if __name__ == "__main__":
    run_summarization_task("sample.pdf")