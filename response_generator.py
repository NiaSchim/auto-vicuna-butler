import queue
import llamacpp
from pathos.pools import ProcessPool
import random
import threading
import csv
import os
import re
import subprocess
import sys
from multiprocessing import Process, Queue
os.environ["PYTHONIOENCODING"] = "utf-8"
import shlex
import re


class ResponseGenerator:
    def __init__(self, model_path):
        self.model_path = model_path
        self.processes = {}
        self.ai_name = self.get_ai_name()
        self.initialize_model()

    def get_ai_name(self):
        try:
            with open("purpose.txt", "r") as f:
                return f.readline().strip()
        except FileNotFoundError:
            return "me"

    def initialize_model(self):
        # Read the second line of the purpose.txt file
        try:
            with open("purpose.txt", "r") as f:
                f.readline()  # Skip the first line (AI name)
                initial_prompt = f.readline().strip()  # Read the second line (initial prompt)
        except FileNotFoundError:
            initial_prompt = ''

        command = [
            "llamacpp-cli",
            "-m", self.model_path,
            "-n", "1",
            "-t", "8",
            "--n_predict", "2048",
            "-c", "2048",
            "--temp", "0.748",
            "--top_k", "40",
            "--top_p", "0.5",
            "--repeat_last_n", "256",
            "-b", "1024",
            "--repeat_penalty", "1.14",
            "-p", f'"{initial_prompt}"'  # Set the initial prompt
        ]
        command_str = " ".join(command)  # Convert the command list to a single string

        print(f"Running command: {command_str}")  # Print the command being run
        process = subprocess.Popen(
            command_str, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
        )
        self.processes[self.model_path] = process

        # Wait for the model to initialize and print every line of the output
        output = process.stdout.readline().decode("utf-8").strip()
        while output:
            print(output)
            if re.match(r".+", output):
                break
            output = process.stdout.readline().decode("utf-8").strip()

    def send_input_to_process(self, process, prompt):
        process.stdin.write(f"{prompt}\n".encode("utf-8"))
        process.stdin.flush()

    def generate_response(self, prompt):
        process = self.processes[self.model_path]

        # Send input to the model and get the response
        self.send_input_to_process(process, prompt)
        response = process.stdout.readline().decode("utf-8").strip()

        return response

    def get_response(self, prompt):
        response = self.generate_response(prompt)
        print(f"You: {prompt}")
        print(f"Generated Response: {response}")
        print("-" * 40)
        return response