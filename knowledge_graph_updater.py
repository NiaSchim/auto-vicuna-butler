import os
import threading
import time
from xml.etree import ElementTree as ET
import sys
from response_generator import ResponseGenerator
import networkx as nx
import multiprocessing as mp
import re


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


def generate_summary(model_instance, text, max_lines=20, max_words=335):
    summary = text
    while True:
        summary_lines = summary.split('\n')
        if len(summary_lines) <= max_lines:
            if len(summary_lines) == 1 and len(summary.split()) > max_words:
                summary = model_instance.generate_response(f"Summarize the following text in less than {max_words} words:\n{summary}")
            else:
                break
        else:
            summary = model_instance.generate_response(f"Summarize the following text in less than {max_lines} lines:\n{summary}")
    return summary


script_dir = os.path.dirname(os.path.abspath(__file__))


class KnowledgeGraphUpdater:
    def __init__(self, model_13b_instance, model_7b_instance):
        self.model_13b_instance = model_13b_instance
        self.model_7b_instance = model_7b_instance
        self.chat_history_file = "chat_history.txt"
        self.shortterm_graph = nx.DiGraph()
        self.longterm_graph = nx.DiGraph()
        self.update_interval = 30
        self.daemon = True
        #commented out to protect the order of operations
        #self.start()

    def start(self):
        try:
            mp.set_start_method('spawn')
        except RuntimeError:
            pass

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

        prompt = f"Given my purpose ('{purpose}'), my 3 goals ({', '.join(goals)}), my short-term memory, and my long-term memory, what goal should I work on next and how?"
        response = self.model_13b_instance.generate_response(prompt)
        print(response)

        # Summarize knowledge graphs, goals, and purpose using the 7b model
        summary_prompt = f"Summarize the following knowledge graphs, goals, and purpose:\n\nKnowledge Graphs:\nShort-term: {self.shortterm_graph}\nLong-term: {self.longterm_graph}\n\nGoals: {', '.join(goals)}\n\nPurpose: {purpose}\n"
        summary = self.model_7b_instance.generate_response(summary_prompt)
        print(summary)

        time.sleep(self.update_interval)

        activities_prompt = "What are you doing?\n"
        activities = self.model_13b_instance.generate_response(activities_prompt)
        print(f"Model 13b:\nInput: {activities_prompt}\nResponse: {activities}\n")

        insights_prompt = "What have you learned about what you're doing?\n"
        insights = self.model_13b_instance.generate_response(insights_prompt)
        print(f"Model 13b:\nInput: {insights_prompt}\nResponse: {insights}\n")

        general_learnings_prompt = "What have you learned in general?\n"
        general_learnings = self.model_13b_instance.generate_response(general_learnings_prompt)
        print(f"Model 13b:\nInput: {general_learnings_prompt}\nResponse: {general_learnings}\n")

        shortterm_graph_path = "shortterm.txt"
        longterm_graph_path = "longterm.txt"

        # Open the chat history file with "a+" mode (create if it doesn't exist and open for reading and appending)
        with open(self.chat_history_file, "a+") as file:
            file.seek(0)  # Move the file cursor to the beginning of the file
            chat_history = file.read()

        # Remove any blank lines
        chat_history = "\n".join([line for line in chat_history.split('\n') if line.strip()])

        # Include chat_history in the text variable
        text = activities + insights + general_learnings + chat_history
        common_words = get_common_words(text)

        with open(shortterm_graph_path, "a") as file:
            for activity in activities:
                if not should_skip_page(activity, common_words):
                    file.write(f"activity: {activity}\n")
            for insight in insights:
                if not should_skip_page(insight, common_words):
                    file.write(f"insight: {insight}\n")

        with open(longterm_graph_path, "a") as file:
            for element in general_learnings:
                if not should_skip_page(element, common_words):
                    file.write(f"general_learning: {element}\n")

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

        # Limit the chat history to the last 20 non-blank lines
        chat_history_lines = chat_history.split('\n')
        last_20_lines = chat_history_lines[-20:]

        # Write the updated chat history back to the file
        with open(self.chat_history_file, "w") as file:
            file.write("\n".join(last_20_lines))

if __name__ == "__main__":
    model_13b_path = "ggml-vicuna-13b-1.1-q4_1.bin"
    model_7b_path = "ggml-vicuna-7b-1.1-q4_0.bin"

    # Get ResponseGenerator instances for 13b and 7b models
    model_13b_instance = ResponseGenerator(os.path.join(script_dir, model_13b_path))
    model_7b_instance = ResponseGenerator(os.path.join(script_dir, model_7b_path))

    # Create the knowledge graph updater instance
    updater = KnowledgeGraphUpdater(model_13b_instance, model_7b_instance)

    # Run the updater once
    updater.start()