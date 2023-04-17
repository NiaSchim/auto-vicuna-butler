#-------------------------------------------------------------------------------
# Name:        autovicuna
# Purpose: awesomeness!!!
#
# Author:      The Schim
#
# Created:     14/04/2023
# Copyright:   (c) The Schim 2023
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from knowledge_graph_updater import KnowledgeGraphUpdater
from queue import Queue
import os
import subprocess
import webbrowser
import tkinter as tk
import sys
from response_generator import ResponseGenerator
from response_generator import ResponseGenerator as response_generator
import multiprocessing as mp
import multiprocessing
import web_browsing_module
import filesystem_module
os.environ["PYTHONIOENCODING"] = "utf-8"
import re

script_dir = os.path.dirname(os.path.abspath(__file__))


class AutoVicuna:
    def __init__(self, model_13b_path, model_7b_path):
        # Set instance variables
        self.model_13b_path = model_13b_path
        self.model_7b_path = model_7b_path

        # Create the chatbot models
        self.model_13b_instance = ResponseGenerator(self.model_13b_path)
        self.model_7b_instance = ResponseGenerator(self.model_7b_path)

        # Create the knowledge graph updater instance and pass the chatbot models to it
        self.knowledge_graph_updater_instance = KnowledgeGraphUpdater(self.model_13b_instance, self.model_7b_instance)

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

        # Main loop for the chatbot's choice of actions
        action_prompt = f"{name}, choose an Option: 1. Browse web 2. file system 3. question\n"
        action_prompt_utf8 = action_prompt.encode('utf-8').decode('utf-8')
        while True:
            chatbot_choice = chatbot_decision = ResponseGenerator(model_13b_path).generate_response(action_prompt_utf8)
            # Extract the first numeric digit from the response as the answer
            answer = re.search('\d', chatbot_choice).group()
            # Move on to the next code
            choice = int(answer)
            if choice == 1:
                web_browsing_module.browse_web(model_13b_path, model_7b_path, knowledge_graph_updater_instance)
            elif choice == 2:
                filesystem_module.auto_vicuna_workflow()
            elif choice == 3:
                question_prompt = f"{name}, ask a question:"
                question = input(question_prompt)  # Use input function to get the question from the user
                response = self.model_13b_instance.generate_response(question)
                self.knowledge_graph_updater_instance.update_knowledge_graphs(response)
            else:
                print("Sorry invalid response, try again.")
            response_13b = self.model_13b_instance.generate_response(action_prompt.encode("utf-8").decode("utf-8"))
            response_7b = self.model_7b_instance.generate_response(action_prompt.encode("utf-8").decode("utf-8"))
            # Update the knowledge graph
            self.knowledge_graph_updater_instance.update_shortterm_graph(response_13b)
            self.knowledge_graph_updater_instance.update_longterm_graph(response_7b)
            break  # exit the loop


if __name__ == "__main__":
    model_13b_path = "ggml-vicuna-13b-1.1-q4_1.bin"
    model_7b_path = "ggml-vicuna-7b-1.1-q4_0.bin"

    # Create instances of AutoVicuna for each model
    autovicuna = AutoVicuna(model_13b_path, model_7b_path)

    # Create the KnowledgeGraphUpdater instance and pass the chatbot models to it
    knowledge_graph_updater_instance = KnowledgeGraphUpdater(model_13b_path, model_7b_path)

    # Run AutoVicuna in a loop to always return to the start() function
    while True:
        autovicuna.start()