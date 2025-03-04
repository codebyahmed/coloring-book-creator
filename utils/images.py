import os
import io
import requests
import time
import pathlib
import base64
from PIL import Image
from dotenv import load_dotenv
from upscale_ncnn_py import UPSCALE
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
load_dotenv()

# Initialize the LLM model for renaming images
llm = ChatOpenAI(model="gpt-4o-mini") #ChatGoogleGenerativeAI(model="gemini-1.5-flash")

# Load the Nebius API token for image generation
NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY")
NEBIUS_API_URL = "https://api.studio.nebius.com/v1/images/generations"
NEBIUS_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "*/*",
    "Authorization": f"Bearer {NEBIUS_API_KEY}"
}

# Initialize the UPSCALE object for upscaling
param_path = "models/SPAN/spanx2_ch48.param"
model_path = "models/SPAN/spanx2_ch48.bin"
upscale = UPSCALE(gpuid=0, model=-1, scale=2)
upscale._load(param_path=pathlib.Path(param_path), model_path=pathlib.Path(model_path), scale=2)


def query(prompt: str) -> bytes:
    """Query the Nebius API to generate an image for the given prompt"""
    payload = {
        "model": "black-forest-labs/flux-dev",
        "response_format": "b64_json",
        "response_extension": "jpg",
        "width": 832,
        "height": 1152,
        "num_inference_steps": 50,
        "negative_prompt": "",
        "seed": -1,
        "prompt": prompt
    }
    response = requests.post(NEBIUS_API_URL, headers=NEBIUS_HEADERS, json=payload, timeout=240)
    response_json = response.json()
    
    # Extract the base64 image data from response and decode
    if "data" in response_json and len(response_json["data"]) > 0:
        if "b64_json" in response_json["data"][0]:
            image_data = base64.b64decode(response_json["data"][0]["b64_json"])
            return image_data
    
    raise Exception(f"Failed to get image data from response: {response_json}")


def make_images(prompts: list[str], topic: str) -> None:
    """Generates, renames and upscales images for the given prompts"""

    # Create a directory for the images
    directory = os.path.join("books", topic, "images")
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Generate images for each prompt
    print("\nGenerating images for each prompt...")
    for i, prompt in enumerate(prompts):
        prompt = topic + " - " + prompt
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
        
        # Rename the image
        image_name = shorten_image_name(prompt)
        image_path = f"./books/{topic}/images/{image_name}.jpeg"
        
        # Upscale the image and save over the original
        try:
            start_time = time.time()
            upscaled_image = upscale.process_pil(image)
            upscaled_image.save(image_path, quality=60)
            end_time = time.time()
            duration = end_time - start_time
            print(f"Time taken to upscale image: {duration:.2f} seconds")
        except Exception as e:
            print(f"Error in upscaling image: {e}")
            # If upscaling fails, save the original image
            image.save(image_path)
    
    print(f"\nImages saved to ./books/{topic}/images")



def shorten_image_name(image_name: str) -> str:
    """Shorten the image name using LLM"""
    template = ChatPromptTemplate([
        ("system", IMAGE_RENAME_SYSTEM_PROMPT),
        ("human", "Filename: {image_name}")
    ])
    success = False
    start_time = time.time()
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
    if shortened_name.endswith("."):
        shortened_name = shortened_name[:-1]
    end_time = time.time()
    duration = end_time - start_time
    print(f"Time taken to rename image: {duration:.2f} seconds")
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

Your response should only be the shortened name of the image.
"""