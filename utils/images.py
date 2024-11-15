import os
import io
import requests
import time
from PIL import Image
from dotenv import load_dotenv
load_dotenv()


HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}


def query(prompt: str) -> bytes:
    """Query the API to generate an image for the given prompt"""
    payload = {
        "inputs": prompt,
        "parameters": {
            "width": 832,
            "height": 1152,
            "num_inference_steps": 50,
        },
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content


def make_images(prompts: list[str], topic: str):
    """Generate images for the given prompts"""

    # Create a directory for the images
    directory = os.path.join("books", topic, "images")
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Generate images for each prompt
    print("\nGenerating images for each prompt...")
    for i, prompt in enumerate(prompts):
        print(f"{i+1}. {prompt}")
        success = False
        start_time = time.time()
        while not success:
            try:
                image_bytes = query(prompt)
                image = Image.open(io.BytesIO(image_bytes))
                success = True
            except Exception as e:
                print(f"An error occurred: {e}. Retrying in 5 seconds...")
                time.sleep(5)
        
        end_time = time.time()
        duration = end_time - start_time
        print(f"Time taken to generate image: {duration:.2f} seconds")
        image.save(f"./books/{topic}/images/{prompt[:100]}.jpeg")
    
    print(f"\nImages saved to ./books/{topic}/images")