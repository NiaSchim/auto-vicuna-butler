from llama import Llama
from multiprocessing import Process, Queue
import sys
import time
from response_generator import ResponseGenerator


def model_runner(model_path):
    model_instance = ResponseGenerator(model_path)
    while True:
        input_text = queue.get()
        if input_text == "stop":
            break
        response = model_instance.generate_response(input_text)
        print(f"\n### Input: {input_text}\n### Reaction: {response}")
        sys.stdout.flush()
        time.sleep(1)


if __name__ == "__main__":
    model_path = input()
    process = Process(target=model_runner, args=(model_path,))
    process.start()
    while True:
        input_text = input()
        if input_text == "stop":
            queue.put("stop")
            break
        queue.put(input_text)