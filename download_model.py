from sentence_transformers import SentenceTransformer
import os

def main():
    """
    Downloads the sentence-transformer model to a local directory
    for offline use.
    """
    # Define the model name and the path to save it
    model_name = 'all-MiniLM-L6-v2'
    model_path = 'models/'

    # Create the directory if it doesn't exist
    if not os.path.exists(model_path):
        os.makedirs(model_path)

    print(f"Downloading model: {model_name}")
    print(f"Saving to: {os.path.abspath(model_path)}")

    # Download and save the model
    model = SentenceTransformer(model_name)
    model.save(model_path)

    print("\nModel downloaded and saved successfully!")
    print("You can now delete this script (download_model.py).")

if __name__ == "__main__":
    main()