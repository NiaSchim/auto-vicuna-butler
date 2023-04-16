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

        self.queue_13b = self.model_13b_instance.queue
        self.queue_7b = self.model_7b_instance.queue

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
        while True:  # Main loop to repeat the process
            # Main loop for the chatbot's choice of actions
            while True:

                purpose_file = "purpose.txt"

                if os.path.exists(purpose_file):
                    with open(purpose_file, "r") as file:
                        lines = file.readlines()
                        name = lines[0].strip()
                        purpose = lines[1].strip()
                        goals = [goal.strip() for goal in lines[2:]]

                # Include the summarized information in the chatbot's input prompt
                action_prompt = f"{name}, choose an action\n\nOptions:\n1. Browse the web\n2. Alter the file system\n3. Ask a question\n\n please pick a number between 1 and 3."
                print(f"Action prompt: {action_prompt}")
                chatbot_choice = self.model_13b_instance.generate_response(action_prompt)

                # Wait for a non-empty response with two newline characters
                while not chatbot_choice.strip() or chatbot_choice.count('\n') < 2:
                    chatbot_choice += self.model_13b_instance.generate_response('')

                choice, *args = chatbot_choice.strip().split()

                if choice == '1':
                    web_browsing_module.browse_web()
                elif choice == '2':
                    filesystem_module.alter_filesystem()
                elif choice == '3':
                    question_prompt = f"{name}, ask a question:"
                    print(f"Question prompt: {question_prompt}")
                    question = self.model_13b_instance.wait_for_response(question_prompt, '\n')
                    print(f"Question: {question}")
                    response = self.model_13b_instance.generate_response(question)
                    print(f"Response: {response}")
                    self.knowledge_graph_updater_instance.update_knowledge_graphs(response)
                else:
                    print("Passing input to both models...")
                    response_13b = self.model_13b_instance.generate_response(action_prompt)
                    print(f"Model 13b:\nInput: {action_prompt}\nResponse: {response_13b}\n")
                    response_7b = self.model_7b_instance.generate_response(action_prompt)
                    print(f"Model 7b:\nInput: {action_prompt}\nResponse: {response_7b}\n")
                    break  # Exit the inner loop to update the knowledge graph

            # Update the knowledge graph
            self.knowledge_graph_updater_instance.update_shortterm_graph(response_13b)
            self.knowledge_graph_updater_instance.update_longterm_graph(response_7b)

if __name__ == "__main__":
    model_13b_path = "ggml-vicuna-13b-1.1-q4_1.bin"
    model_7b_path = "ggml-vicuna-7b-1.1-q4_0.bin"

    # Set start method for multiprocessing
    try:
        mp.set_start_method('spawn')
    except RuntimeError:
        pass

    # Create the AutoVicuna instance
    auto_vicuna = AutoVicuna(model_13b_path, model_7b_path)

    # Run AutoVicuna in a loop to always return to the start() function
    while True:
        auto_vicuna.__init__(model_13b_path, model_7b_path)
        auto_vicuna.start()