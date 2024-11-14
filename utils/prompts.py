import threading
import queue
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")

class Categories(BaseModel):
    categories: list[str] = Field(description="List of categories for the topic")

class Prompts(BaseModel):
    prompts: list[str] = Field(description="List of prompts for each category")


def generate_categories(topic: str) -> list[str]:
    """Generate categories for the given topic"""
    template = ChatPromptTemplate([
        ("system", CREATE_CATEGORIES_SYSTEM_PROMPT),
        ("human", "The topic is {topic}")
    ])
    prompt = template.invoke({
        "topic": topic
    })
    structured_llm = llm.with_structured_output(Categories)
    response = structured_llm.invoke(prompt)
    categories = response.categories
    return categories


def generate_prompts(topic: str, category: str, prompts: queue.Queue) -> None:
    """Generate prompts for the given category"""
    template = ChatPromptTemplate([
        ("system", CREATE_PROMPTS_SYSTEM_PROMPT),
        ("human", "The topic is {topic}, and the category is {category}")
    ])
    prompt = template.invoke({
        "topic": topic,
        "category": category
    })
    structured_llm = llm.with_structured_output(Prompts)
    response = structured_llm.invoke(prompt)
    for p in response.prompts: # Add prompts to queue
        prompts.put(p)
    print(f"{category} | \u2713")


def make_prompts(topic: str) -> list[str]:
    """Generate categories and prompts for the given topic"""
    # Generate categories for the given topic
    print("\nGenerating categories for the given topic...")
    categories = generate_categories(topic)

    # Display the generated categories
    for i, category in enumerate(categories):
        print(f"{i+1}. {category}")

    # Generate prompts for each category (use threading for parallel execution)
    print("\nGenerating prompts for each category...")
    threads = []
    prompts = queue.Queue()
    for category in categories:
        thread = threading.Thread(target=generate_prompts, args=(topic, category, prompts))
        thread.start()
        threads.append(thread)
    
    #Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Save the generated prompts to a csv file
    with open(f"books/{topic}/prompts.csv", "w") as f:
        f.write("No.\tPrompt\n")
        i = 1
        while not prompts.empty():
            prompt = prompts.get()
            f.write(f"{i}\t{topic}: {prompt}\n") # Add topic before each prompt
            i += 1
    
    print(f"\nPrompts saved to ./books/{topic}/prompts.csv")
    return prompts


################################################################ PROMPTS ################################################################


CREATE_CATEGORIES_SYSTEM_PROMPT = """
You are a creative designer tasked with generating 14 unique and engaging category ideas for a coloring book based on the given topic.

### Guidelines for Generating Categories:

1. **Broad and Imaginative:** Create categories that offer diverse illustration possibilities.
2. **Varied Scenes:** Ensure each category provides multiple potential scene or pose variations.
3. **Aspect Capturing:** Focus on capturing different aspects, emotions, or contexts related to the topic.
4. **Visual Appeal:** Categories should be visually interesting and appeal to various age groups.
5. **Simplicity:** Ensure the categories are easy to understand and can be easily depicted by image generation models.

### Output Requirements:

- **Numbered List:** Provide a non-numbered list of 14 distinct categories.
- **Descriptive Phrases:** Each category should be a descriptive, evocative phrase.
- **Showcase Versatility:** Categories should showcase the topic's versatility.
- **Avoid Repetition:** Avoid repetitive or overly similar concepts.

### Example:

**Topic:** Cats
1. **Playtime Adventures:** Cats playing with various toys and objects.
2. **Sleepy Moments:** Cats in different cozy sleeping positions.
3. **Seasonal Fun:** Cats participating in different seasonal activities.

**Important:** Be creative, unexpected, and ensure each category offers rich potential for engaging coloring book illustrations.
"""


CREATE_PROMPTS_SYSTEM_PROMPT = """
You are an advanced language model tasked with generating 5 detailed prompts for creating illustrations suitable for a coloring book page based on the given topic and category. \
The illustrations should be minimalist in style, featuring clear outlines with thick lines on a white background, making them easy for young kids to color.

**Guidelines for generating prompts:**

1. Each prompt should be descriptive enough to convey the scene or concept clearly.
2. Focus on simple shapes and forms that can be easily understood and colored by children.
3. Ensure that the prompts encourage creativity and imagination while remaining straightforward.
4. Provide a variety of scenes or concepts within the given category to showcase its diversity.
5. The final illustrations should be engaging and visually appealing, suitable for young audiences.

**Output Requirements:**

* A non-nnumbered list of 5 distinct prompts.
* Each prompt should be a clear, engaging sentence or two that encapsulates the scene to be illustrated.
* Each prompt should specify that the illustrations should be minimalist in style, featuring clear outlines with thick lines on a white background, making them easy for young kids to color.

**Important:** Be imaginative, concise, and ensure each prompt is easy to visualize for creating a coloring page that kids will enjoy.

**Example Category: Animals**
1. A cheerful lion with a fluffy golden mane, standing proudly on a small rock in a simple jungle setting filled with green leaves and soft sunlight filtering through the trees. \
The lion's expression should be friendly and inviting, with big, bright eyes and a wide smile. The illustration should be minimalist in style, featuring clear, bold outlines with \
thick lines on a clean white background, making it easy for young kids to color. The jungle elements should be simplified, allowing for easy coloring without intricate details.
2. A playful dolphin leaping gracefully out of the sparkling blue water, with a few stylized waves and bubbles surrounding it. The dolphin should be depicted mid-jump, with a \
joyful expression and a shiny, smooth body. The background should include a bright sun and a few fluffy clouds, adding to the cheerful atmosphere. The illustration should be \
minimalist in style, featuring clear, bold outlines with thick lines on a clean white background, making it easy for young kids to color. The water elements should be simplified to enhance the coloring experience.
3. A charming group of three little ducks swimming happily in a serene pond, surrounded by tall green reeds and a few floating lily pads. Each duck should have a different \
expression and pose, showcasing their playful nature. The pond should have gentle ripples to indicate movement, and the background should include a soft blue sky with a few fluffy clouds. \
The illustration should be minimalist in style, featuring clear, bold outlines with thick lines on a clean white background, making it easy for young kids to color. The natural elements should be simplified to facilitate an enjoyable coloring experience.
"""