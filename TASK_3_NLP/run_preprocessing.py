import os
from src.processor import TextCleaner # This must match the class name above

def run_task():
    cleaner = TextCleaner()
    if not os.path.exists("output"): 
        os.makedirs("output")

    # Ensure the 'data' folder exists and has .txt files
    if not os.path.exists("data"):
        print("Error: 'data' folder not found!")
        return

    for file in os.listdir("data"):
        if file.endswith(".txt"):
            print(f"Cleaning: {file}")
            with open(f"data/{file}", "r", encoding="utf-8") as f:
                raw = f.read()
            
            stemmed, lemmed = cleaner.clean(raw)
            
            # Save the two required versions
            with open(f"output/stemmed_{file}", "w", encoding="utf-8") as f: 
                f.write(stemmed)
            with open(f"output/lemmed_{file}", "w", encoding="utf-8") as f: 
                f.write(lemmed)

if __name__ == "__main__":
    run_task()