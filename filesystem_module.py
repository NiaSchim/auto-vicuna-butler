import os
import threading
from queue import Queue
from knowledge_graph_updater import KnowledgeGraphUpdater
import sys
import response_generator

script_dir = os.path.dirname(os.path.abspath(__file__))


def create_file(filename):
    with open(filename, 'w') as file:
        print(f"File '{filename}' created successfully.")

def read_file(filename):
    if os.path.isfile(filename):
        with open(filename, 'r') as file:
            content = file.read()
            print(f"Content of '{filename}':\n{content}")
    else:
        print(f"File '{filename}' not found.")

def update_file(filename, content):
    if os.path.isfile(filename):
        with open(filename, 'a') as file:
            file.write(content)
            print(f"Content added to '{filename}'.")
    else:
        print(f"File '{filename}' not found.")

def delete_file(filename):
    if os.path.isfile(filename):
        os.remove(filename)
        print(f"File '{filename}' deleted successfully.")
    else:
        print(f"File '{filename}' not found.")

def list_files_and_folders():
    print("Current directory content:")
    for item in os.listdir():
        print(item)

def create_new_folder():
    folder_name = input("Enter the name of the new folder: ")
    try:
        os.makedirs(folder_name)
        print(f"Folder '{folder_name}' created successfully.")
    except FileExistsError:
        print(f"Folder '{folder_name}' already exists.")
    except Exception as e:
        print(f"Error creating folder '{folder_name}': {e}")

def navigate_to_directory(auto_vicuna_playground_path):
    new_directory = input("Enter the path of the directory to navigate to: ")
    new_directory = os.path.abspath(new_directory)
    if not new_directory.startswith(auto_vicuna_playground_path):
        print(f"Navigation to '{new_directory}' is not allowed. Please stay within the '{auto_vicuna_playground_path}' directory.")
        return

    if os.path.exists(new_directory) and os.path.isdir(new_directory):
        os.chdir(new_directory)
        print(f"Successfully navigated to '{new_directory}'.")
    else:
        print(f"Directory '{new_directory}' not found.")

def auto_vicuna_workflow(bin_path, model_13b):
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

    while True:
        # Summarize knowledge graphs, goals, and purpose using the 7b model
        summary_prompt = f"Summarize the following knowledge graphs, goals, and purpose:\n\nKnowledge Graphs:\n{knowledge_graph_updater}\nGoals:\n{', '.join(goals)}\nPurpose:\n{purpose}\n"
        summary = response_generator.get_response(os.path.join(script_dir, model_7b), prompt)
        interim = response_generator.get_response(os.path.join(script_dir, model_13b), prompt)
        decision_prompt = "Choose an action for file system operations:\n1. Create a file\n2. Read a file\n3. Update a file\n4. Delete a file\n5. List files and folders\n6. Navigate to a directory\n7. Create new folder\n8. Nevermind"
        chatbot_decision = response_generator.get_response(os.path.join(script_dir, model_13b), prompt)

        choice, *args = chatbot_decision.split()

        if choice == '1':
            filename_prompt = "Enter the filename:"
            filename = response_generator.get_response(os.path.join(script_dir, model_13b), prompt)
            create_file(filename.strip())
        elif choice == '2':
            filename_prompt = "Enter the filename:"
            filename = response_generator.get_response(os.path.join(script_dir, model_13b), prompt)
            read_file(filename.strip())
        elif choice == '3':
            filename_prompt = "Enter the filename:"
            filename = response_generator.get_response(os.path.join(script_dir, model_13b), prompt)
            content_prompt = "Enter the content to update the file:"
            content = response_generator.get_response(os.path.join(script_dir, model_13b), prompt)
            update_file(filename.strip(), content.strip())
        elif choice == '4':
            filename_prompt = "Enter the filename:"
            filename = response_generator.get_response(os.path.join(script_dir, model_13b), prompt)
            delete_file(filename.strip())
        elif choice == '5':
            list_files_and_folders()
        elif choice == '6':
            new_directory_prompt = "Enter the new directory path:"
            new_directory = response_generator.get_response(os.path.join(script_dir, model_13b), prompt)
            navigate_to_directory(new_directory.strip())
        elif choice == '7':
            create_new_folder()
        elif choice == '8':
            print("Exiting the file system operations.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    bin_path = os.path.dirname(os.path.abspath(__file__))
    model_13b = "ggml-vicuna-13b-1.1-q4_1.bin"
    model_7b = "ggml-vicuna-7b-1.1-q4_0.bin"

    auto_vicuna_playground = "AutoVicunaPlayground"
    auto_vicuna_playground_path = os.path.abspath(auto_vicuna_playground)
    os.makedirs(auto_vicuna_playground_path, exist_ok=True)
    os.chdir(auto_vicuna_playground_path)

    auto_vicuna_workflow(bin_path, model_13b, model_7b)