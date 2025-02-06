# Coloring Book Creator

Effortlessly generate unique, child-friendly coloring book pages on any topic you choose. Perfect for creating custom coloring books for kids. Creates 150 black and white coloring pages per topic.

> **Note:** You must have a Vulkan-compatible GPU to run this project for SPAN to upscale the images.

## How to Run

1. **Clone the repository:**
    ```sh
    git clone https://github.com/codebyahmed/coloring-book-creator.git
    cd coloring-book-creator
    ```

2. **Create a virtual environment and activate it:**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages:**
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**
    - Create a `.env` file in the root directory.
    - Add your Hugging Face API token:
        ```
        HF_TOKEN=your_hugging_face_api_token
        ```
    - Add your OpenAI API token:
        ```
        OPENAI_API_KEY=your_open_ai_api_key
        ```

5. **Run the application:**
    ```sh
    python main.py
    ```
    - Enter the topic name for the coloring book when prompted.

6. **Wait for the coloring pages to be generated:**
    - The generated pages will be saved in the `./books/<topic_name>/images` directory.

## Technologies Used

- **Flux1 dev** from Hugging Face for creating images.
- **OpenAI** for generating categories and prompts for images.
- **LangChain** for integrating with OpenAI (can easily switch to Gemini if needed).
- **SPAN** for upscaling the images by 2x.

## Project Structure

```
.gitignore
main.py
models/
    SPAN/ # Upscaling model
README.md
requirements.txt
utils/
    __init__.py
    images.py # Generate images and upscale
    prompts.py # Generate categories and prompts
```

## Contributing

Feel free to open issues or submit pull requests if you have any suggestions or improvements.