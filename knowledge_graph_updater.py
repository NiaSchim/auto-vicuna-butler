import os
import threading
import time
from xml.etree import ElementTree as ET
import sys
from response_generator import ResponseGenerator
import networkx as nx
import multiprocessing as mp

# Helper functions
def count_common_words(page, common_words):
    word_count = 0
    for word in common_words:
        word_count += page.lower().count(word.lower())
    return word_count

def should_skip_page(page, common_words, threshold=0.05):
    total_word_count = len(page.split())
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

script_dir = os.path.dirname(os.path.abspath(__file__))
class KnowledgeGraphUpdater:
    def __init__(self, model_13b_instance, model_7b_instance):
        self.model_13b_instance = model_13b_instance
        self.model_7b_instance = model_7b_instance

        self.shortterm_graph = nx.DiGraph()
        self.longterm_graph = nx.DiGraph()
        self.update_interval = 30
        self.daemon = True
        self.start()

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

if __name__ == "__main__":
    model_13b_path = "ggml-vicuna-13b-1.1-q4_1.bin"
    model_7b_path = "ggml-vicuna-7b-1.1-q4_0.bin"

    # Get ResponseGenerator instances for 13b and 7b models
    model_13b_instance = ResponseGenerator(os.path.join(script_dir, model_13b_path))
    model_7b_instance = ResponseGenerator(os.path.join(script_dir, model_7b_path))

    # Create the knowledge graph updater instance
    updater = KnowledgeGraphUpdater(model_13b_instance, model_7b_instance)

    # Get response from the 13b model
    response_13b = model_13b_instance.generate_response(user_input)

    # Get response from the 7b model
    response_7b = model_7b_instance.generate_response(user_input)

    # Print the responses
    print("13b:", response_13b)
    print("7b:", response_7b)

    # Update the knowledge graphs
    updater.update_shortterm_graph(response_13b)
    updater.update_longterm_graph(response_7b)