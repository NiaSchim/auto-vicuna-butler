import requests
from bs4 import BeautifulSoup
import threading
from queue import Queue
import os
from knowledge_graph_updater import KnowledgeGraphUpdater
import sys
import response_generator

script_dir = os.path.dirname(os.path.abspath(__file__))

def browse_web(chatbot):
    current_url = ""
    browsing_history = []
    page_content = ""
    current_page = 0
    content_chunks = []

    # Change token_limit as needed
    token_limit = 2048

    while True:
        decision_prompt = "Choose an action for web browsing:\n0. Read unsummarized\n1. Summarize page\n2. Follow hyperlink\n3. Enter URL\n4. Last page (if applicable)\n5. Next page (if applicable)\n6. Exit browsing session"
        chatbot_decision = response_generator.get_response(os.path.join(script_dir, model_13b), prompt)

        choice, *args = chatbot_decision.split()

        if choice == '0':
            print(content_chunks[current_page])
        elif choice == '1':
            summary = response_generator.get_response(os.path.join(script_dir, model_7b), prompt)
            print(f"Summary of the page:\n{summary}")
        elif choice == '2':
            hyperlink_prompt = "Enter the hyperlink:"
            hyperlink = response_generator.get_response(os.path.join(script_dir, model_13b), prompt).strip()
            current_url = hyperlink
            page_content = fetch_page_content(current_url)
            content_chunks = split_content_into_chunks(page_content, token_limit)
            current_page = 0
            browsing_history.append(current_url)
        elif choice == '3':
            url_prompt = "Enter the URL:"
            url = response_generator.get_response(os.path.join(script_dir, model_13b), prompt).strip()
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
            print("Invalid choice. Please try again.")


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
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    bin_path = os.path.dirname(os.path.abspath(__file__))
    model_13b = "ggml-vicuna-13b-1.1-q4_1.bin"
    model_7b = "ggml-vicuna-7b-1.1-q4_0.bin"
    queue_13b = Queue()
    queue_7b = Queue()

    browse_web()
