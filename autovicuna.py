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
import multiprocessing as mp
import multiprocessing
import web_browsing_module
import filesystem_module
os.environ["PYTHONIOENCODING"] = "utf-8"
import re
from knowledge_graph_updater import KnowledgeGraphUpdater
from web_browsing_module import browse_web
from filesystem_module import auto_vicuna_workflow

script_dir = os.path.dirname(os.path.abspath(__file__))


class AutoVicuna:
    def __init__(self, model_13b_path, model_7b_path, knowledge_graph_updater_instance):
        # Set instance variables
        self.model_13b_path = model_13b_path
        self.model_7b_path = model_7b_path
        self.knowledge_graph_updater_instance = knowledge_graph_updater_instance

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

        # Main loop for the chatbot's choice of actions
        while True:
            # Prompt the user to choose an action
            action_prompt = f"{name}, choose an Option: 1. Browse web 2. file system 3. question\n"
            action_prompt_utf8 = action_prompt.encode('utf-8').decode('utf-8')
            # Use the 13B model to generate a response to the prompt
            chatbot_choice = self.model_13b_instance.generate_response(action_prompt_utf8)
            # Extract the first numeric digit from the response as the answer
            answer_match = re.search('\d', chatbot_choice)
            if answer_match is None:
                # If no digit is found, prompt the user to enter a valid number between 1 and 3
                print("Sorry, I didn't understand your choice. Please enter a number between 1 and 3.")
                continue
            answer = answer_match.group()
            # Convert the answer to an integer and check if it's between 1 and 3
            choice = int(answer)
            if choice < 1 or choice > 3:
                # If the choice is not between 1 and 3, prompt the user to enter a valid number
                print("Please enter a number between 1 and 3.")
                continue
            # If the choice is valid, execute the corresponding action
            print(f"Selected choice: {choice}")  # Print the selected choice
            if choice == 1:
                web_browsing_module.browse_web(response_generator_big, response_generator_fast, knowledge_graph_updater_instance)
            elif choice == 2:
                filesystem_module.auto_vicuna_workflow(response_generator_big, response_generator_fast)
            elif choice == 3:
                question_prompt = f"{name}, ask a question:"
                question = input(question_prompt)  # Use input function to get the question from the user
                response = response_generator_big(question)
                self.knowledge_graph_updater_instance.summarize_and_store(response)
            else:
                print("Sorry invalid response, try again.")
            break  # exit the loop
            self.knowledge_graph_updater_instance.start()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    model_7b_path = "ggml-vicuna-7b-1.1-q4_0.bin"
    model_13b_path = "ggml-vicuna-13b-1.1-q4_1.bin"
    # Create a new instance of ResponseGenerator
    response_generator_big = ResponseGenerator(model_13b_path)

    # Create a new new instance of ResponseGenerator
    response_generator_fast = ResponseGenerator(model_7b_path)

    knowledge_graph_updater_instance = KnowledgeGraphUpdater(response_generator_big, response_generator_fast)
    web_browsing_module = browse_web(response_generator_big, response_generator_fast, knowledge_graph_updater_instance)
    filesystem_module = auto_vicuna_workflow(response_generator_big, response_generator_fast)


    # Create an instance of AutoVicuna and pass the KnowledgeGraphUpdater instance
    autovicuna = AutoVicuna(model_13b_path, model_7b_path, knowledge_graph_updater_instance)

    # Run AutoVicuna in a loop to always return to the start() function
    while True:
        autovicuna.start()