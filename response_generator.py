from pathos.multiprocessing import ProcessPool
import queue
import llamacpp
import os
import random
import multiprocessing as mp
import time

class ResponseGenerator:
    def __init__(self, model_path):
        self.model_path = model_path
        self.lock = mp.Lock()
        self.prompt_queue = queue.Queue()
        self.model_queue = queue.Queue()
        self.process = None
        self.model = self.initialize_model()

    def _init_process_pool(self):
        if self.process is None:
            self.process = ProcessPool(processes=1)
            self.process.apipe(self.continuous_model_runner)

    def initialize_model(self):
        def progress_callback(progress):
            pass

        params = llamacpp.InferenceParams.default_with_callback(progress_callback)
        params.path_model = self.model_path
        params.seed = random.randint(10000, 99999)
        params.repeat_penalty = 1.0
        model = llamacpp.LlamaInference(params)
        return model

    def continuous_model_runner(self):
        while True:
            input_text = self.prompt_queue.get()
            if input_text == "stop":
                break
            with self.lock:
                response = self.generate_response(input_text)
            print(f"Model: {self.model_path}")
            print(f"Input: {input_text}")
            print(f"Response: {response}")
            print("-" * 40)
            self.model_queue.put(response)

    def generate_response(self, prompt):
        self._init_process_pool()

        ai_name = ''
        if os.path.exists("purpose.txt"):
            with open("purpose.txt", "r") as file:
                ai_name = file.readline().strip()
        print(f"to {ai_name}: {prompt}")
        prompt = f"{ai_name}: {prompt}"
        prompt_tokens = self.model.tokenize(prompt, True)
        self.model.update_input(prompt_tokens)
        self.model.ingest_all_pending_input()

        response = ""
        last_non_empty_time = time.monotonic()
        non_empty_since_newline = False
        while True:
            self.model.eval()
            token = self.model.sample()
            text = self.model.token_to_str(token)
            if text == "\n":
                if non_empty_since_newline:
                    break
                else:
                    continue
            if text.strip():
                last_non_empty_time = time.monotonic()
                non_empty_since_newline = True
            response += text
            if time.monotonic() - last_non_empty_time > 1.0:
                break
        print(f"from {ai_name}: {response}")
        return response.strip()

    def get_response(self, prompt):
        self.prompt_queue.put(prompt)
        response = self.model_queue.get()
        self.update_chat_history(prompt, response)
        print(f"User: {prompt}")
        print(f"Generated Response: {response}")
        print("-" * 40)
        return response

    def update_chat_history(self, prompt, response):
        if not os.path.exists("chat_history.txt"):
            with open("chat_history.txt", "w") as file:
                pass

        with open("chat_history.txt", "r") as file:
            chat_lines = file.readlines()

        chat_lines.append(f"User: {prompt[:47]}{'...' if len(prompt) > 50 else ''}\n")
        chat_lines.append(f"Generated Response: {response[:47]}{'...' if len(response) > 50 else ''}\n")

        while len(chat_lines) > 5:
            chat_lines.pop(0)

        with open("chat_history.txt", "w") as file:
            file.writelines(chat_lines)

    def build_initial_prompt(self):
        initial_prompt = ""

        if os.path.exists("purpose.txt"):
            with open("purpose.txt", "r") as file:
                lines = file.readlines()
                for i, line in enumerate(lines[:5], start=1):
                    initial_prompt += f"goal#{i}: {line.strip()}\n"

        for filename in ["longterm_summary.txt", "shortterm_summary.txt"]:
            content = ""
            if os.path.exists(filename):
                with open(filename, "r") as file:
                    content = file.read().replace('\n', '\t')
            initial_prompt += f"{filename[:-4]}: {content}\n"

        if os.path.exists("chat_history.txt"):
            with open("chat_history.txt", "r") as file:
                content = file.read().replace('\n', '\t')
            initial_prompt += f"chatlog: {content}\n"

        return initial_prompt

if __name__ == "__main__":
    model_path = "ggml-vicuna-7b-1.1-q4_0.bin"
    response_generator = ResponseGenerator(model_path)
    initial_prompt = response_generator.build_initial_prompt()

    while True:
        user_input = input("Enter your prompt: ")
        if user_input.lower() == "exit":
            break
        prompt = initial_prompt + f"now: {user_input}"
        response_generator.get_response(prompt)

