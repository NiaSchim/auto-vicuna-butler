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
import threading
from queue import Queue
import os
import subprocess
import webbrowser
import tkinter as tk
import sys
from llama_cpp import Llama  # Import Llama class
import response_generator

script_dir = os.path.dirname(os.path.abspath(__file__))


def auto_vicuna_workflow(bin_path, model_13b, model_7b, queue_13b, queue_7b):
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
        print("An experimental, open-source AI application called AutoVicuna that leverages the power of the ggml-vicuna model to assist you with tasks.")

        purpose = input("What's my purpose? ")

        print("Give me 3 goals:")
        goals = [input(f"{i+1}. ") for i in range(3)]

        with open(purpose_file, "w") as file:
            file.write(f"{name}\n{purpose}\n")
            file.writelines([f"{goal}\n" for goal in goals])

    prompt = f"Given my purpose ('{purpose}'), my 3 goals ({', '.join(goals)}), my short-term memory, and my long-term memory, what goal should I work on next and how?"
    response = response_generator.get_response(os.path.join(script_dir, model_13b), prompt)
    print(response)
    knowledge_graph_updater = KnowledgeGraphUpdater(bin_path, model_13b, model_7b)

    # Summarize knowledge graphs, goals, and purpose using the 7b model
    summary_prompt = f"Summarize the following knowledge graphs, goals, and purpose:\n\nKnowledge Graphs:\n{knowledge_graph_updater}\nGoals:\n{', '.join(goals)}\nPurpose:\n{purpose}\n"
    summary = response_generator.get_response(os.path.join(script_dir, model_7b), prompt)
    print(summary)

    # Main loop for the chatbot's choice of actions
    while True:
        # Include the summarized information in the chatbot's input prompt
        action_prompt = f"{name}, choose an action given the following information:\n\n{summary}\n\nOptions:\n1. Browse the web\n2. Alter the file system\n3. Ask a question\n4. Exit\n"
        # Ask the chatbot to choose an action
        action_prompt = f"{name}, choose an action:\n1. Browse the web\n2. Alter the file system\n3. Ask a question\n4. Exit\n"
        chatbot_choice = response_generator.get_response(os.path.join(script_dir, model_13b), prompt)
        print(chatbot_choice)

        if chatbot_choice.strip() == '1':
            web_browsing_module.browse_web()
        elif chatbot_choice.strip() == '2':
            filesystem_module.alter_filesystem()
        elif chatbot_choice.strip() == '3':
            question_prompt = f"{name}, ask a question:"
            question = response_generator.get_response(os.path.join(script_dir, model_13b), prompt)
            print(question)
            response = response_generator.get_response(os.path.join(script_dir, model_13b), prompt)
            print(response)
            knowledge_graph_updater.update_knowledge_graphs(response)
        else:
            print("Invalid choice. Please try again.")


def browse_folder():
    root = tk.Tk()
    root.withdraw()

    folder_path = filedialog.askdirectory()
    return folder_path

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.dirname(os.path.abspath(__file__))
    model_13b_path = "ggml-vicuna-13b-1.1-q4_1.bin"
    model_7b_path = "ggml-vicuna-7b-1.1-q4_0.bin"

    # Create Llama instances for 13b and 7b models
    model_13b_instance = Llama(model_path=os.path.join(model_path, model_13b_path))
    model_7b_instance = Llama(model_path=os.path.join(model_path, model_7b_path))

    # Create queues for passing prompts to the 13b and 7b model instances
    queue_13b = Queue()
    queue_7b = Queue()

    # Start the continuous processes
    model_13b_thread = threading.Thread(target=continuous_model_runner, args=(model_13b_instance, queue_13b))
    model_7b_thread = threading.Thread(target=continuous_model_runner, args=(model_7b_instance, queue_7b))
    model_13b_thread.start()
    model_7b_thread.start()

    auto_vicuna_workflow(model_13b_instance, model_7b_instance, queue_13b, queue_7b)

    # Exit the continuous processes
    queue_13b.put("EXIT")
    queue_7b.put("EXIT")
    model_13b_thread.join()
    model_7b_thread.join()