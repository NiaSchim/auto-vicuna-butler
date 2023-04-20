# filesystem.py
import os
import re

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

def auto_vicuna_workflow(response_generator_big, response_generator_fast, knowledge_graph_updater_instance):
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

    while True:
        decision_prompt = "Choose an action for file system operations, please pick only a single digit lonely numbered response. 1. Create a file\n2. Read a file 3. Update a file 4. Delete a file 5. List files and folders 6. Navigate to a directory 7. Create new folder 8. Nevermind\n"
        print(f"Decision prompt: {decision_prompt}")
        decision_prompt_utf8 = decision_prompt.encode("utf-8").decode("utf-8")
        chatbot_decision = response_generator_big.generate_response(decision_prompt_utf8)

        # Extract the first numeric digit from the response as the answer
        answer = re.search('\d', chatbot_decision).group()
        print(f"Answer: {answer}")

        # Move on to the next code
        choice = int(answer)
        valid_options = ['1', '2', '3', '4', '5', '6', '7', '8']
        while choice not in valid_options:
            user_input = response_generator_big.wait_for_response(chatbot_decision, '\n').strip()
            try:
                choice = user_input.strip().split()[0]
            except IndexError:
                print("Sorry invalid response, try again.")
                continue

            if choice not in valid_options:
                print("Sorry invalid response, try again.")
                continue

            if choice == '1':
                print(f"Selected choice: {choice}")  # Print the selected choice
                filename_prompt = "Enter the filename:"
                filename = response_generator_big.wait_for_response(filename_prompt, '\n').strip()
                create_file(filename)
            elif choice == '2':
                print(f"Selected choice: {choice}")  # Print the selected choice
                filename_prompt = "Enter the filename:"
                filename = response_generator_big.wait_for_response(filename_prompt, '\n').strip()
                read_file(filename)
            elif choice == '3':
                print(f"Selected choice: {choice}")  # Print the selected choice
                filename_prompt = "Enter the filename:"
                filename = response_generator_big.generate_response(filename_prompt, '\n').strip()
                content_prompt = "Enter the content to update the file:"
                content = response_generator_big.generate_response(content_prompt, '\n').strip()
                update_file(filename, content)
            elif choice == '4':
                print(f"Selected choice: {choice}")  # Print the selected choice
                filename_prompt = "Enter the filename:"
                filename = response_generator_big.generate_response(filename_prompt, '\n').strip()
                delete_file(filename)
            elif choice == '5':
                print(f"Selected choice: {choice}")  # Print the selected choice
                list_files_and_folders()
            elif choice == '6':
                print(f"Selected choice: {choice}")  # Print the selected choice
                new_directory_prompt = "Enter the new directory path:"
                new_directory = response_generator_big.generate_response(new_directory_prompt, '\n').strip()
                navigate_to_directory(auto_vicuna_playground_path, new_directory)
            elif choice == '7':
                create_new_folder()
                print(f"Selected choice: {choice}")  # Print the selected choice
            elif choice == '8':
                print(f"Selected choice: {choice}")  # Print the selected choice
                print("Exiting the file system operations.")
                break
            knowledge_graph_updater_instance.summarize_and_store()
