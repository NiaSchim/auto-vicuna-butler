# response_generator.py
import multiprocessing
from queue import Queue
from llama_cpp import Llama

instances = {}
queues = {}
processes = {}


def get_instance(model_path):
    if model_path not in instances:
        instances[model_path] = Llama(model_path=model_path)
        queues[model_path] = multiprocessing.Queue()
        processes[model_path] = multiprocessing.Process(target=continuous_model_runner, args=(instances[model_path], queues[model_path], model_path))
        processes[model_path].daemon = True
        processes[model_path].start()
    return instances[model_path], queues[model_path]


def continuous_model_runner(model_instance, queue, model_path):
    model_name = model_path.split('/')[-1]
    if model_name == "ggml-vicuna-7b-1.1-q4_0.bin":
        print("Short-term mem:")
    elif model_name == "ggml-vicuna-13b-1.1-q4_1.bin":
        print("Main attention:")

    while True:
        prompt = queue.get()
        if prompt == "EXIT":
            break
        response = generate_response(model_instance, prompt)
        print(response)

    print("Process terminated.")


def generate_response(model_instance, prompt):
    response = model_instance(prompt, max_tokens=100, stop=["\n### Input: ", "\n### Reaction: "], echo=True)
    return response["choices"][0]["text"]


def get_response(model_path, prompt):
    model_instance, queue = get_instance(model_path)
    queue.put(prompt)
    return generate_response(model_instance, prompt)