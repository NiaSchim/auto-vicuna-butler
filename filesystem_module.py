import os
import threading
from queue import Queue

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

def navigate_to_directory():
    new_directory = input("Enter the path of the directory to navigate to: ")
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
    response = run_main_exe(prompt, bin_path, model_13b, queue_13b)
    print(response)
    knowledge_graph_updater = KnowledgeGraphUpdater()

    while True:
        # Summarize knowledge graphs, goals, and purpose using the 7b model
        summary_prompt = f"Summarize the following knowledge graphs, goals, and purpose:\n\nKnowledge Graphs:\n{knowledge_graph_updater}\nGoals:\n{', '.join(goals)}\nPurpose:\n{purpose}\n"
        summary = run_main_exe(bin_path, model_7b, summary_prompt, queue_7b)
        interim = run_main_exe(bin_path, model_13b, summary, queue_13b)
        decision_prompt = "Choose an action for file system operations:\n1. Create a file\n2. Read a file\n3. Update a file\n4. Delete a file\n5. List files and folders\n6. Navigate to a directory\n7. Nevermind"
        chatbot_decision = run_main_exe(bin_path, model_13b, decision_prompt, queue_13b)

        choice, *args = chatbot_decision.split()

        if choice == '1':
            filename_prompt = "Enter the filename:"
            filename = run_main_exe(bin_path, model_13b, filename_prompt, queue_13b)
            content_prompt = "Write the file in the proper file format:"
            content = run_main_exe(bin_path, model_13b, content_prompt, queue_13b)
            create_file(filename.strip(), content.strip())
            break
        elif choice == '2':
            filename_prompt = "Enter the filename:"
            filename = run_main_exe(bin_path, model_13b, filename_prompt, queue_13b)
            read_file(filename.strip())
            break
        elif choice == '3':
            filename_prompt = "Enter the filename:"
            filename = run_main_exe(bin_path, model_13b, filename_prompt, queue_13b)
            content_prompt = "Enter the content to update the file:"
            content = run_main_exe(bin_path, model_13b, content_prompt, queue_13b)
            update_file(filename.strip(), content.strip())
            break
        elif choice == '4':
            filename_prompt = "Enter the filename:"
            filename = run_main_exe(bin_path, model_13b, filename_prompt, queue_13b)
            delete_file(filename.strip())
            break
        elif choice == '5':
            list_files_and_folders()
            break
        elif choice == '6':
            new_directory_prompt = "Enter the new directory path:"
            new_directory = run_main_exe(bin_path, model_13b, new_directory_prompt, queue_13b)
            navigate_to_directory(new_directory.strip())
            break
        elif choice == '7':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    bin_path = "."
    model_13b = "ggml-vicuna-13b-1.1-q4_1.bin"
    model_7b = "ggml-vicuna-7b-1.1-q4_0.bin"
    working_directory = browse_folder()
    os.chdir(working_directory)

    auto_vicuna_workflow(bin_path, model_13b, model_7b)