import os
from utils import make_prompts, make_images

if __name__ == '__main__':
    topic = input("Please enter the topic name: ")

    # Create a directory for the given topic
    directory = os.path.join("books", topic)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Generate prompts for the given topic
    prompts = make_prompts(topic)

    # Generate images for the given prompts
    make_images(prompts, topic)

