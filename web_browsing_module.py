import requests
from bs4 import BeautifulSoup
import threading
from queue import Queue
import os
from knowledge_graph_updater import KnowledgeGraphUpdater
import sys
from response_generator import ResponseGenerator as response_generator
import ResponseGenerator

script_dir = os.path.dirname(os.path.abspath(__file__))

def browse_web(model_13b_path, model_7b_path):
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
        decision_prompt = "Choose an action for web browsing, please pick only a single digit lonely numbered response;\n0. Read unsummarized\n1. Summarize page\n2. Follow hyperlink\n3. Enter URL\n4. Last page (if applicable)\n5. Next page (if applicable)\n6. Exit browsing session"
        chatbot_decision = input(f"{decision_prompt}\n>>> ")

        # Collect the first numeric input
        choice = None
        while not choice:
            choice = chatbot_decision.strip()[0] if chatbot_decision.strip().isdigit() else None
            if not choice:
                chatbot_choice = model_13b_instance.ResponseGenerator.generate_response(action_prompt)
                while '\n' not in chatbot_choice:
                    chatbot_choice += model_13b_instance.generate_response(action_prompt)

        # Prompt the AI based on the user's choice
        if choice == '0':
            print(content_chunks[current_page])
        elif choice == '1':
            prompt = "Summarize the current page."
            summary = model_7b_instance.generate_response(prompt)
            print(f"Model 7b:\nInput: {prompt}\nResponse: {summary}\n")
        elif choice == '2':
            hyperlink_prompt = "Enter the hyperlink:"
            hyperlink = input(f"{hyperlink_prompt}\n>>> ").strip()
            current_url = hyperlink
            page_content = fetch_page_content(current_url)
            content_chunks = split_content_into_chunks(page_content, token_limit)
            current_page = 0
            browsing_history.append(current_url)
        elif choice == '3':
            url_prompt = "Enter the URL:"
            url = input(f"{url_prompt}\n>>> ").strip()
            current_url = url
            page_content = fetch_page_content(current_url)
            content_chunks = split_content_into_chunks(page_content, token_limit)
            current_page = 0
            browsing_history.append(current_url)
        elif choice == '4':
            if current_page > 0:
                current_page -= 1
            else:
                print("Cannot go back to the last page.")
        elif choice == '5':
            if current_page < len(content_chunks) - 1:
                current_page += 1
            else:
                print("Cannot go to the next page.")
        elif choice == '6':
            break
        else:
            print("Passing input to both models...")
            response_13b = model_13b_instance.generate_response(decision_prompt)
            print(f"Model 13b:\nInput: {decision_prompt}\nResponse: {response_13b}\n")
            response_7b = model_7b_instance.generate_response(decision_prompt)
            print(f"Model 7b:\nInput: {decision_prompt}\nResponse: {response_7b}\n")

            # Wait for a non-empty response
            chatbot_choice = self.model_13b_instance.generate_response(action_prompt)
            while '\n' not in chatbot_choice:
                chatbot_choice += model_13b_instance.generate_response(action_prompt)

            choice, *args = chatbot_choice.split()

    # Terminate the processes
    model_13b_instance.queue.put("EXIT")
    model_7b_instance.queue.put("EXIT")

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

    # Call the browse_web function
    browse_web(chatbot_13b, chatbot_7b)