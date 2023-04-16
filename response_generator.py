import queue
import sys
import llamacpp
from pathos.pools import ProcessPool
import random


class ResponseGenerator:
    def __init__(self, model_path):
        self.model_path = model_path

        self.queue = queue.Queue()

        self.process = ProcessPool(processes=1)
        self.process.apipe(self.continuous_model_runner, self.queue)

        self.model = self.initialize_model()

    def initialize_model(self):
        def progress_callback(progress):
            pass

        params = llamacpp.InferenceParams.default_with_callback(progress_callback)
        params.path_model = self.model_path
        params.seed = random.randint(10000, 99999)
        params.repeat_penalty = 1.0
        model = llamacpp.LlamaInference(params)
        return model

    def continuous_model_runner(self, queue):
        while True:
            input_text = queue.get()
            if input_text == "stop":
                break
            response = self.generate_response(input_text)
            print(f"Model: {self.model_path}")
            print(f"Input: {input_text}")
            print(f"Response: {response}")
            print("-" * 40)

    def generate_response(self, prompt):
        with open("purpose.txt", "r") as file:
            ai_name = file.readline().strip()

        prompt = f"{ai_name}: {prompt}"
        prompt_tokens = self.model.tokenize(prompt, True)
        self.model.update_input(prompt_tokens)
        self.model.ingest_all_pending_input()

        response = ""
        while True:
            self.model.eval()
            token = self.model.sample()
            text = self.model.token_to_str(token)
            if text == "\n":
                break
            response += text

        return response.strip()

    def wait_for_response(self, prompt, delimiter='\n'):
        response = ''
        newline_count = 0

        while newline_count < 2:
            response += input(prompt + ' ')
            if response.endswith(delimiter):
                newline_count += 1
            prompt = ''

        return response

    def get_response(self, prompt):
        self.queue.put(prompt)
        response = self.queue.get()
        print(f"User: {prompt}")
        print(f"Generated Response: {response}")
        print("-" * 40)
        return response