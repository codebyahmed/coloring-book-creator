import os
import io
import requests
import time
from PIL import Image
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

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
    response = requests.post(API_URL, headers=headers, json=payload, timeout=240)
    return response.content


def make_images(prompts: list[str], topic: str) -> None:
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
                print(f"Error in generating image: {e}. Retrying in 5 seconds...")
                time.sleep(5)
        
        end_time = time.time()
        duration = end_time - start_time
        print(f"Time taken to generate image: {duration:.2f} seconds")
        image_name = shorten_image_name(prompt)
        image.save(f"./books/{topic}/images/{image_name}.jpeg")
    
    print(f"\nImages saved to ./books/{topic}/images")


def shorten_image_name(image_name: str) -> str:
    """Shorten the image name using gemini"""
    template = ChatPromptTemplate([
        ("system", IMAGE_RENAME_SYSTEM_PROMPT),
        ("human", "Filename: {image_name}")
    ])
    success = False
    while not success:
        try:
            prompt = template.invoke({
                "image_name": image_name
            })
            response = llm.invoke(prompt)
            shortened_name = response.content
            success = True
        except Exception as e:
            print(f"Error in naming image: {e}. Retrying in 5 seconds...")
            time.sleep(5)
    # Remove 'Spaces and Enter' from the end of image name if any
    shortened_name = shortened_name.strip()
    shortened_name = shortened_name.replace("\n", "")
    shortened_name = shortened_name.replace("\r", "")
    return shortened_name


IMAGE_RENAME_SYSTEM_PROMPT = """
Your task is to rename a file by shortening its current name without losing essential meaning.

Please follow these guidelines:
* The shortened name should be in Title Case in which the first letter of each word is capitalized.
* Ensure the shortened name is concise and informative.
* Avoid abbreviations that could confuse the user.
* Maintain clarity and meaningfulness of the file name.

Example:
Original file name: "Tweety Bird: A nighttime scene featuring Tweety Bird flying playfully among large, puffy clouds, with a backdrop of a bright full moon and scattered stars. Minimalist details outline coloring pages on a white background. Ensure the image is drawn as a clear outline with thick lines, making it easy for young kids to color."
Shortened file name: "Tweety Bird In A Starry Night Sky."

Please generate the shortened file name according to the guidelines above.
"""