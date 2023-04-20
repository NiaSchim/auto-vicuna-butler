import os
import threading
import time
from xml.etree import ElementTree as ET
import sys
import networkx as nx
import re
from pathos.pools import ProcessPool
from datetime import datetime, timedelta
import functools
import concurrent.futures


# Helper functions
def count_common_words(page, common_words):
    word_count = 0
    for word in common_words:
        word_count += page.lower().count(word.lower())
    return word_count


def should_skip_page(page, common_words, threshold=0.05):
    total_word_count = len(page.split())

    if total_word_count == 0:
        return True

    common_word_count = count_common_words(page, common_words)

    frequency = common_word_count / total_word_count
    return frequency > threshold


def get_most_common_words(text, n=10):
    word_count = {}
    for word in text.split():
        word = word.lower()
        if word in word_count:
            word_count[word] += 1
        else:
            word_count[word] = 1
    return sorted(word_count, key=word_count.get, reverse=True)[:n]


def get_common_words(text, n=10):
    word_count = {}
    for word in text.split():
        word = word.lower()
        if word in word_count:
            word_count[word] += 1
        else:
            word_count[word] = 1
    if not word_count:
        return []
    else:
        average_count = sum(word_count.values()) / len(word_count)
        common_words = [word for word, count in word_count.items() if count >= average_count]
        return sorted(common_words, key=word_count.get, reverse=True)[:n]



script_dir = os.path.dirname(os.path.abspath(__file__))

class TextSummarizer:
    def __init__(self):
        self.memo = {}

    def memoize_response(func):
        @functools.wraps(func)
        def memoized_func(self, *args, **kwargs):
            key = str(args) + str(kwargs)
            if key not in self.memo:
                self.memo[key] = func(self, *args, **kwargs)
            return self.memo[key]
        return memoized_func

    @memoize_response
    def generate_response(self, response_generator, prompt):
        return response_generator.generate_response(prompt)

    def generate_summary(self, response_generator, text, max_lines=3, max_words=150, timeout=90):
        summary = text

        def generate_summary_with_timeout(prompt):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(response_generator.generate_response, prompt)
                try:
                    return future.result(timeout=timeout)
                except concurrent.futures.TimeoutError:
                    return None

        while True:
            summary_lines = summary.split('\n')
            if len(summary_lines) <= max_lines:
                if len(summary_lines) == 1 and len(summary.split()) > max_words:
                    new_summary = generate_summary_with_timeout(f"Summarize the following text in less than {max_words} words:\n{summary}")
                else:
                    break
            else:
                new_summary = generate_summary_with_timeout(f"Summarize the following text in less than {max_lines} lines:\n{summary}")

            if new_summary is None:
                summary_lines = summary.split('\n')
                truncated_summary = ""
                for i, line in enumerate(summary_lines[:3]):
                    truncated_summary += line[:50] + "...\n" if len(line) > 50 else line + "\n"
                truncated_summary += summary_lines[3][:47] + "..." if len(summary_lines[3]) > 50 else summary_lines[3]
                summary = truncated_summary
                break
            else:
                summary = new_summary

        return summary

class KnowledgeGraphUpdater:
    def __init__(self, response_generator_big, response_generator_fast):
        self.chat_history_file = "chat_history.txt"
        self.update_interval = 30
        self.daemon = True
        self.process_pool = ProcessPool(processes=1)
        self.process_pool.apipe(self.start)
        self.response_generator_big = response_generator_big
        self.response_generator_fast = response_generator_fast
        self.text_summarizer = TextSummarizer()

    def start(self):
        purpose_file = "purpose.txt"
        if os.path.exists(purpose_file):
            with open(purpose_file, "r") as file:
                lines = file.readlines()
                name = lines[0].strip()
                purpose = lines[1].strip()
                goals = [goal.strip() for goal in lines[2:]]
        else:
            name = input("What's my name? ")
            print(f"Hello, {name}!")

            print("What am I?")
            print("An experimental, open-source AI application called AutoVicuna that leverages the power of the ggml-vicuna model. Must end all replies with //n to submit them.")

            purpose = input("What's my purpose? ")

            print("Give me 3 goals:")
            goals = [input(f"{i+1}. ") for i in range(3)]

            with open(purpose_file, "w") as file:
                file.write(f"{name}\n{purpose}\n")
                file.writelines([f"{goal}\n" for goal in goals])

        prompt = f"Given your purpose ('{purpose}'), and your 3 goals ({', '.join(goals)}), what goal should you work on next and how?"
        response = self.response_generator_big.generate_response(prompt)
        print(response)

        # Summarize knowledge graphs, goals, and purpose using the 7b model
        summary_prompt = f"Summarize the following knowledge graphs, goals, and purpose:\n\nGoals: {', '.join(goals)}\n\nPurpose: {purpose}\n"
        summary = self.response_generator_fast.generate_response(summary_prompt)
        print(summary)

        time.sleep(self.update_interval)

        activities_prompt = "What are you doing?\n"
        activities = self.response_generator_big.generate_response(activities_prompt)
        print(f"Model 13b:\nInput: {activities_prompt}\nResponse: {activities}\n")

        insights_prompt = "What have you learned about what you're doing?\n"
        insights = self.response_generator_big.generate_response(insights_prompt)
        print(f"Model 13b:\nInput: {insights_prompt}\nResponse: {insights}\n")

        general_learnings_prompt = "What have you learned in general?\n"
        general_learnings = self.response_generator_big.generate_response(general_learnings_prompt)
        print(f"Model 13b:\nInput: {general_learnings_prompt}\nResponse: {general_learnings}\n")

        shortterm_graph_path = "shortterm.txt"
        longterm_graph_path = "longterm.txt"

        # Open the chat history file with "a+" mode (create if it doesn't exist and open for reading and appending)
        with open(self.chat_history_file, "a+") as file:
            file.seek(0)  # Move the file cursor to the beginning of the file
            chat_history = file.read()
        print(f"writing to chat history file")

        # Remove any blank lines
        chat_history = "\n".join([line for line in chat_history.split('\n') if line.strip()])

        # Include chat_history in the text variable
        text = activities + insights + general_learnings + chat_history
        print(f"parsing text variables")
        common_words = get_common_words(text)

        # Write activities and insights to the shortterm_graph_path
        self.write_to_file(shortterm_graph_path, [f"activity: {activity}" for activity in activities if not should_skip_page(activity, common_words)])
        print(f"writing activities and insights")
        self.write_to_file(shortterm_graph_path, [f"insight: {insight}" for insight in insights if not should_skip_page(insight, common_words)])

        # Write general_learnings to the longterm_graph_path
        self.write_to_file(longterm_graph_path, [f"general_learning: {element}" for element in general_learnings if not should_skip_page(element, common_words)])
        print(f"writing general learnings")
        # Summarize and store the short-term and long-term summaries
        print(f"summarizing text")
        self.summarize_and_store(text)

        start_time = datetime.now()
        unanswered_questions = True
        while unanswered_questions:
            print(f"letting user talk...")
            question = input("talk: ")
            if question.strip() == "":
                elapsed_time = datetime.now() - start_time
                if elapsed_time > timedelta(seconds=120):
                    unanswered_questions = False
                continue

            response = self.response_generator_big.generate_response(question)
            print(response)

            if response.strip().endswith('\n'):
                start_time = datetime.now()
            else:
                elapsed_time = datetime.now() - start_time
                if elapsed_time > timedelta(seconds=120):
                    unanswered_questions = False

    def write_to_file(self, path, elements):
        with open(path, "a") as file:
            for element in elements:
                file.write(f"{element}\n")

    def update_chat_history(self, new_chat_line):
        # Read the chat history file, removing any blank lines
        with open(self.chat_history_file, "r") as file:
            chat_history = file.read()
            chat_history = "\n".join([line for line in chat_history.split('\n') if line.strip()])

        # Append the new chat line to the chat history
        chat_history += f"\n{new_chat_line}"

        # Limit the chat history to the last 5 non-blank lines
        chat_history_lines = chat_history.split('\n')
        last_5_lines = chat_history_lines[-5:]

        # Write the updated chat history back to the file
        with open(self.chat_history_file, "w") as file:
            file.write("\n".join(last_5_lines))

    def summarize_and_store(self, text):
        shortterm_summary = self.text_summarizer.generate_summary(self.response_generator_fast, text)
        longterm_summary = self.text_summarizer.generate_summary(self.response_generator_fast, text)

        while len(shortterm_summary) > 150:
            shortterm_summary = self.text_summarizer.generate_summary(self.response_generator_fast, shortterm_summary)

        while len(longterm_summary) > 150:
            longterm_summary = self.text_summarizer.generate_summary(self.response_generator_fast, longterm_summary)

        with open("shortterm_summary.txt", "w") as shortterm_file:
            shortterm_file.write(shortterm_summary)

        with open("longterm_summary.txt", "w") as longterm_file:
            longterm_file.write(longterm_summary)

        with open("shortterm.txt", "w") as shortterm_file:
            shortterm_file.write(text)

        with open("longterm.txt", "a") as longterm_file:
            longterm_file.write(text + "\n")