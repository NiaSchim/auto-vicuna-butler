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

import threading
from queue import Queue
import os
import subprocess
import webbrowser
import tkinter as tk

def continuous_model_runner(model, bin_path, queue):
    while True:
        prompt = queue.get()
        if prompt == "EXIT":
            break
        response = run_main_exe(bin_path, model, prompt, queue)
        print(response)

    print(f"{model} process terminated.")

def run_main_exe(bin_path, model, prompt, queue):
    queue.put(prompt)
    command = [
        bin_path + "/main.exe",
        # (Remaining command arguments)
        "-m", bin_path + "/" + model
    ]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        print(f"An error occurred: {stderr.decode()}")
    else:
        return stdout.decode()

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
    response = run_main_exe(prompt, bin_path, model_13b, queue_13b)
    print(response)
    knowledge_graph_updater = KnowledgeGraphUpdater()

    # Summarize knowledge graphs, goals, and purpose using the 7b model
    summary_prompt = f"Summarize the following knowledge graphs, goals, and purpose:\n\nKnowledge Graphs:\n{knowledge_graph_updater}\nGoals:\n{', '.join(goals)}\nPurpose:\n{purpose}\n"
    summary = run_main_exe(bin_path, model_7b, summary_prompt, queue_7b)
    print(summary)

    # Main loop for the chatbot's choice of actions
    while True:
        # Include the summarized information in the chatbot's input prompt
        action_prompt = f"{name}, choose an action given the following information:\n\n{summary}\n\nOptions:\n1. Browse the web\n2. Alter the file system\n3. Ask a question\n4. Exit\n"
        # Ask the chatbot to choose an action
        action_prompt = f"{name}, choose an action:\n1. Browse the web\n2. Alter the file system\n3. Ask a question\n4. Exit\n"
        chatbot_choice = run_main_exe(bin_path, model_13b, action_prompt, queue_13b)
        print(chatbot_choice)

        if chatbot_choice.strip() == '1':
            web_browsing_module.browse_web()
        elif chatbot_choice.strip() == '2':
            filesystem_module.alter_filesystem()
        elif chatbot_choice.strip() == '3':
            question_prompt = f"{name}, ask a question:"
            question = run_main_exe(bin_path, model_13b, question_prompt, queue_13b)
            print(question)
            response = run_main_exe(bin_path, model_13b, prompt, queue_13b)
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
    bin_path = "."
    model_13b = "ggml-vicuna-13b-1.1-q4_1.bin"
    model_7b = "ggml-vicuna-7b-1.1-q4_0.bin"
    os.chdir(working_directory)

    # Create queues for passing prompts to the 13b and 7b model processes
    queue_13b = Queue()
    queue_7b = Queue()

    # Start the continuous processes
    model_13b_thread = threading.Thread(target=continuous_model_runner, args=(model_13b, bin_path, queue_13b))
    model_7b_thread = threading.Thread(target=continuous_model_runner, args=(model_7b, bin_path, queue_7b))
    model_13b_thread.start()
    model_7b_thread.start()

    auto_vicuna_workflow(bin_path, model_13b, model_7b, queue_13b, queue_7b)

    # Exit the continuous processes
    queue_13b.put("EXIT")
    queue_7b.put("EXIT")
    model_13b_thread.join()
    model_7b_thread.join()