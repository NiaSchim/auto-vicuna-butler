import requests
from bs4 import BeautifulSoup
import threading
from queue import Queue
import os
import sys
import re
from web_browser_utils import fetch_page_content
from knowledge_graph_updater import KnowledgeGraphUpdater


script_dir = os.path.dirname(os.path.abspath(__file__))


def browse_web(response_generator_big, response_generator_fast, knowledge_graph_updater_instance):
    default_url = 'https://www.wolframalpha.com/'
    current_url = default_url
    browsing_history = [default_url]
    page_content = fetch_page_content(current_url)
    page_storage = {default_url: page_content}
    current_page = 0
    content_chunks = []

    # Change token_limit as needed
    token_limit = 2048

    def extract_links(content):
        soup = BeautifulSoup(content, 'html.parser')
        links = [link.get('href') for link in soup.find_all('a')]
        return links

    while True:
        # Prompt the user to choose an action
        decision_prompt = "Choose an action for web browsing, please pick only a single digit lonely numbered response; 0. Read unsummarized 1. Summarize page 2. Follow hyperlink 3. Enter URL 4. Last page (if applicable) 5. Next page (if applicable) 6. Exit browsing session\n"
        decision_prompt_utf8 = decision_prompt.encode("utf-8").decode("utf-8")
        chatbot_decision = response_generator_big.generate_response(decision_prompt_utf8)

        # Extract the first numeric digit from the response as the answer
        answer_match = re.search('\d', chatbot_decision)
        if answer_match is None:
            # If no digit is found, prompt the user to enter a valid number between 0 and 6
            print("Sorry, I didn't understand your choice. Please enter a number between 0 and 6.")
            continue
        answer = answer_match.group()
        # Convert the answer to an integer and check if it's between 0 and 6
        choice = int(answer)
        if choice < 0 or choice > 6:
            # If the choice is not between 0 and 6, prompt the user to enter a valid number
            print("Please enter a number between 0 and 6.")
            continue
        # If the choice is valid, execute the corresponding action
        print(f"Selected choice: {choice}")  # Print the selected choice

        # Prompt the AI
        if choice == 0:
            print("Unsummarized content:")
            if current_page >= 0 and current_page < len(content_chunks):
                print(content_chunks[current_page])
            else:
                print("Invalid page number")
        elif choice == 1:
            prompt = "Summarize the current page."
            print("Content to summarize:")
            print(page_content)
            summary = response_generator_fast.generate_response(prompt)
            print(f"Model 7b:\nInput: {prompt}\nResponse: {summary}\n")
        elif choice == 2:
            # Display all hyperlinks in the current page content as a list
            hyperlinks = extract_links(page_content)
            print("Available hyperlinks:")
            for i, link in enumerate(hyperlinks):
                print(f"{i+1}. {link}")

            hyperlink_prompt = "Enter the hyperlink:"
            hyperlink = response_generator_fast.generate_response(hyperlink_prompt).strip()

            # Set the new current webpage to the web address of the first valid URL found in the AI's response
            url_match = re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', hyperlink)
            if url_match:
                new_url = url_match.group()
                try:
                    new_page_content = fetch_page_content(new_url)
                    current_url = new_url
                    page_content = new_page_content
                    browsing_history.append(current_url)
                    page_storage[current_url] = page_content
                except Exception as e:
                    print(f"Error fetching the new page: {e}")
                    print("Reverting to the last valid webpage.")
            else:
                print("No valid URL found in the AI's response. Reverting to the last valid webpage.")
        elif choice == 3:
            url_prompt = "Please enter the URL."
            invalid_attempts = 0
            while invalid_attempts < 3:
                url = response_generator_fast.generate_response(url_prompt).strip()
                if not url:
                    continue  # Skip empty URLs
                url_match = re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url)
                if url_match:
                    valid_url = url_match.group()
                    try:
                        new_page_content = fetch_page_content(valid_url)
                        current_url = valid_url
                        page_content = new_page_content
                        browsing_history.append(current_url)
                        page_storage[current_url] = page_content
                        break  # If the URL is valid, exit the loop
                    except Exception as e:
                        print(f"Error fetching the new page: {e}")
                        print("Please try again.")
                        invalid_attempts += 1
                else:
                    print("Invalid URL. Please try again.")
                    invalid_attempts += 1
            if invalid_attempts == 3:
                print("Reached maximum invalid URL attempts. Reverting to the last valid webpage.")
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
        knowledge_graph_updater_instance.summarize_and_store(page_content) if choice == 1 else knowledge_graph_updater_instance.start()  # Update the knowledge graph

def split_content_into_chunks(content, token_limit):
    tokens = content.split()
    chunks = []

    while tokens:
        chunk_tokens = tokens[:token_limit]
        tokens = tokens[token_limit:]
        chunk = ' '.join(chunk_tokens)
        chunks.append(chunk)

    return chunks

def web_browsing_workflow(response_generator_big, response_generator_fast, knowledge_graph_updater_instance):
    browse_web(response_generator_big, response_generator_fast, knowledge_graph_updater_instance)