# filesystem.py
import os
from response_generator import ResponseGenerator
import ResponseGenerator

script_dir = os.path.dirname(os.path.abspath(__file__))
model_13b = "ggml-vicuna-13b-1.1-q4_1.bin"
model_7b = "ggml-vicuna-7b-1.1-q4_0.bin"
response_generator = ResponseGenerator()

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

def auto_vicuna_workflow(model_13b_path, model_7b_path):
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

    response_generator_13b = ResponseGenerator(model_13b_path)
    response_generator_7b = ResponseGenerator(model_7b_path)
    knowledge_graph_updater = KnowledgeGraphUpdater(model_13b_path, model_7b_path)

    while True:
        decision_prompt = "Choose an action for file system operations, please pick only a single digit lonely numbered response.\n1. Create a file\n2. Read a file\n3. Update a file\n4. Delete a file\n5. List files and folders\n6. Navigate to a directory\n7. Create new folder\n8. Nevermind"
        print(f"Decision prompt: {decision_prompt}")
        chatbot_decision = response_generator_13b.generate_response(decision_prompt)

        # Wait for a non-empty response that ends with a newline character
        choice = ''
        while not choice.strip() or not choice.endswith('\n'):
            choice = chatbot_decision.strip()

        choice = choice.strip().split()[0]

        if choice == '1':
            filename_prompt = "Enter the filename:"
            filename = response_generator_13b.wait_for_response(filename_prompt, '\n').strip()
            create_file(filename)
        elif choice == '2':
            filename_prompt = "Enter the filename:"
            filename = response_generator_13b.wait_for_response(filename_prompt, '\n').strip()
            read_file(filename)
        elif choice == '3':
            filename_prompt = "Enter the filename:"
            filename = response_generator_13b.wait_for_response(filename_prompt, '\n').strip()
            content_prompt = "Enter the content to update the file:"
            content = response_generator_13b.wait_for_response(content_prompt, '\n').strip()
            update_file(filename, content)
        elif choice == '4':
            filename_prompt = "Enter the filename:"
            filename = response_generator_13b.wait_for_response(filename_prompt, '\n').strip()
            delete_file(filename)
        elif choice == '5':
            list_files_and_folders()
        elif choice == '6':
            new_directory_prompt = "Enter the new directory path:"
            new_directory = response_generator_13b.wait_for_response(new_directory_prompt, '\n').strip()
            navigate_to_directory(auto_vicuna_playground_path, new_directory)
        elif choice == '7':
            create_new_folder()
        else:
            print("Passing input to both models...")
            response_13b = response_generator_13b.generate_response(decision_prompt)
            print(f"Model 13b:\nInput: {decision_prompt}\nResponse: {response_13b}\n")
            response_7b = response_generator_7b.generate_response(decision_prompt)
            print(f"Model 7b:\nInput: {decision_prompt}\nResponse: {response_7b}\n")

        if choice == '8':
            print("Exiting the file system operations.")
            break

    # Terminate the processes
    model_13b_instance.queue.put("stop")
    model_7b_instance.queue.put("stop")
    model_13b_instance.process.join()
    model_7b_instance.process.join()

if __name__ == "__main__":
    model_13b_path = "ggml-vicuna-13b-1.1-q4_1.bin"
    model_7b_path = "ggml-vicuna-7b-1.1-q4_0.bin"

    # Get ResponseGenerator instances for 13b and 7b models
    model_13b_instance = response_generator(os.path.join(model_13b_path))
    model_7b_instance = response_generator(os.path.join(model_7b_path))

    # Send prompts to the models
    model_13b_instance.get_response("hello, world.")
    model_7b_instance.get_response("world, hello.")

    auto_vicuna_workflow(model_13b_instance, model_7b_instance)