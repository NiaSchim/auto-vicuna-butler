import requests
from bs4 import BeautifulSoup
import threading
from queue import Queue
import os
from knowledge_graph_updater import KnowledgeGraphUpdater
import sys
from response_generator import ResponseGenerator as response_generator
from response_generator import ResponseGenerator
import re
from web_browser_utils import fetch_page_content
import re

script_dir = os.path.dirname(os.path.abspath(__file__))

def fetch_page_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract visible text
        visible_text = soup.get_text().strip()

        # Extract image descriptions
        image_descriptions = []
        images = soup.find_all('img')
        for img in images:
            alt_text = img.get('alt')
            if alt_text:
                image_descriptions.append(alt_text.strip())

        # Extract file links
        file_links = []
        file_elements = soup.find_all(['a', 'img'])
        for element in file_elements:
            href = element.get('href')
            src = element.get('src')
            if href and '.' in href.split('/')[-1]:
                file_links.append(href)
            elif src and '.' in src.split('/')[-1]:
                file_links.append(src)

        # Format output as CSV
        output = f"{visible_text}\n"
        output += ",".join(image_descriptions) + "\n"
        output += ",".join(file_links) + "\n"
        return output
    except Exception as e:
        print("Error while fetching page content:", e)
        return None

def browse_web(model_13b_path, model_7b_path, knowledge_graph_updater_instance):
    current_url = ""
    browsing_history = []
    page_content = ""
    current_page = 0
    content_chunks = []

    # Change token_limit as needed
    token_limit = 2048

    # Get ResponseGenerator instances for 13b and 7b models
    model_13b_instance = ResponseGenerator(os.path.join(model_13b_path))
    model_7b_instance = ResponseGenerator(os.path.join(model_7b_path))

    while True:
        decision_prompt = "Choose an action for web browsing, please pick only a single digit lonely numbered response; 0. Read unsummarized 1. Summarize page 2. Follow hyperlink 3. Enter URL 4. Last page (if applicable) 5. Next page (if applicable) 6. Exit browsing session\n"
        print(f"Decision prompt: {decision_prompt}")
        decision_prompt_utf8 = decision_prompt.encode("utf-8").decode("utf-8")
        chatbot_decision = ResponseGenerator(model_13b_path).generate_response(decision_prompt_utf8)

        # Extract the first numeric digit from the response as the answer
        answer = re.search('\d', chatbot_decision).group()
        print(f"Answer: {answer}")

        # Move on to the next code
        choice = int(answer)
        while not choice:
            user_input = input(chatbot_decision)
            try:
                choice = int(user_input)
            except ValueError:
                print("Sorry invalid response, try again.")
                continue

            if choice < 0 or choice > 6:
                print("Sorry invalid response, try again.")
                choice = None

        # Prompt the AI based on the user's choice
        if choice == 0:
            print(content_chunks[current_page])
        elif choice == 1:
            prompt = "Summarize the current page."
            summary = model_7b_instance.generate_response(prompt)
            print(f"Model 7b:\nInput: {prompt}\nResponse: {summary}\n")
        elif choice == 2:
            hyperlink_prompt = "Enter the hyperlink:"
            hyperlink = input(f"{hyperlink_prompt}\n>>> ").strip()
            current_url = hyperlink
            page_content = fetch_page_content(current_url)
            visible_text, image_descriptions, file_links = page_content.strip().split("\n")
            content_chunks = split_content_into_chunks(visible_text, token_limit)
            current_page = 0
            browsing_history.append(current_url)
        elif choice == 3:
            url_prompt = "Enter the URL:"
            url = input(f"{url_prompt}\n>>> ").strip()
            current_url = hyperlink
            page_content = fetch_page_content(current_url)
            visible_text, image_descriptions, file_links = page_content.strip().split("\n")
            content_chunks = split_content_into_chunks(visible_text, token_limit)
            current_page = 0
            browsing_history.append(current_url)
        elif choice == 4:
            if current_page > 0:
                current_page -= 1
            else:
                print("Cannot go back to the last page.")
        elif choice == 5:
            if current_page < len(content_chunks) - 1:
                current_page += 1
            else:
                print("Cannot go to the next page.")
        elif choice == 6:
            break

        print("Exiting the loop to update the knowledge graph...")
        response_13b = model_13b_instance.generate_response(decision_prompt)
        print(f"Model 13b:\nInput: {decision_prompt}\nResponse: {response_13b}\n")
        response_7b = model_7b_instance.generate_response(decision_prompt)
        print(f"Model 7b:\nInput: {decision_prompt}\nResponse: {response_7b}\n")

        # Call the update_knowledge_graphs method of the KnowledgeGraphUpdater instance
        knowledge_graph_updater_instance.update_knowledge_graphs(response_13b, response_7b)

def split_content_into_chunks(content, token_limit):
    tokens = content.split()
    chunks = []

    while tokens:
        chunk_tokens = tokens[:token_limit]
        tokens = tokens[token_limit:]
        chunk = ' '.join(chunk_tokens)
        chunks.append(chunk)

    return chunks

if __name__ == "__main__":
    model_13b_path = "ggml-vicuna-13b-1.1-q4_1.bin"
    model_7b_path = "ggml-vicuna-7b-1.1-q4_0.bin"

    # Create instances of the ResponseGenerator class
    chatbot_13b = response_generator(os.path.join(script_dir, model_13b_path))
    chatbot_7b = response_generator(os.path.join(script_dir, model_7b_path))

    # Create the KnowledgeGraphUpdater instance and pass the chatbot models to it
    knowledge_graph_updater_instance = KnowledgeGraphUpdater(chatbot_13b, chatbot_7b)

    # Call the browse_web function with the KnowledgeGraphUpdater instance
    browse_web(chatbot_13b, chatbot_7b, knowledge_graph_updater_instance)