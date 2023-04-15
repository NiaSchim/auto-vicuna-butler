import os
import threading
import time
from xml.etree import ElementTree as ET
from queue import Queue
from chatbot import Chatbot  # Assuming there's an existing chatbot implementation
from keyword_extraction import extract_keywords  # Assuming there's a keyword extraction method
from entity_alignment import align_entities  # Assuming there's an entity alignment method


def run_main_exe(bin_path, model, prompt, queue):
    queue.put(prompt)
    command = [
        bin_path + "main.exe",
        "-m", bin_path + "/" + model
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        print(f"An error occurred: {stderr.decode()}")
    else:
        return stdout.decode()


class KnowledgeGraphUpdater:

    def __init__(self, bin_path, model_13b, model_7b, longterm_file='longterm.xml', shortterm_file='shortterm.xml', update_interval=300):
        self.bin_path = bin_path
        self.model_13b = model_13b
        self.model_7b = model_7b
        self.longterm_file = longterm_file
        self.shortterm_file = shortterm_file
        self.update_interval = update_interval

        self._initialize_knowledge_graphs()

        self._updater_thread = threading.Thread(target=self._update_knowledge_graphs, daemon=True)
        self._updater_thread.start()

    def _initialize_knowledge_graphs(self):
        if not os.path.exists(self.longterm_file):
            root = ET.Element('knowledge')
            tree = ET.ElementTree(root)
            tree.write(self.longterm_file)

        if not os.path.exists(self.shortterm_file):
            root = ET.Element('insights')
            tree = ET.ElementTree(root)
            tree.write(self.shortterm_file)

    def _update_knowledge_graphs(self):
        while True:
            time.sleep(self.update_interval)

            activities = run_main_exe(self.bin_path, self.model_13b, "What are you doing?", Queue())
            insights = run_main_exe(self.bin_path, self.model_13b, "What have you learned about what you're doing?", Queue())
            general_learnings = run_main_exe(self.bin_path, self.model_13b, "What have you learned in general?", Queue())

            self._update_shortterm_graph(extract_keywords(activities), extract_keywords(insights))

            shortterm_general_learnings = run_main_exe(self.bin_path, self.model_7b, "What have you learned in general, given your insight graph?", Queue())
            longterm_general_learnings = run_main_exe(self.bin_path, self.model_7b, "What have you learned in general, given your general knowledge graph?", Queue())

            aligned_elements = align_entities(shortterm_general_learnings, longterm_general_learnings)
            self._update_longterm_graph(aligned_elements)

    def _update_shortterm_graph(self, activities, insights):
        tree = ET.parse(self.shortterm_file)
        root = tree.getroot()

        for activity in activities:
            element = ET.SubElement(root, 'activity')
            element.text = activity

        for insight in insights:
            element = ET.SubElement(root, 'insight')
            element.text = insight

        tree.write(self.shortterm_file)

    def _update_longterm_graph(self, aligned_elements):
        tree = ET.parse(self.longterm_file)
        root = tree.getroot()

        for element in aligned_elements:
            aligned_element = ET.SubElement(root, 'aligned_element')
            aligned_element.text = element

        tree.write(self.longterm_file)

if name == 'main':
    bin_path = ""
    model_13b = "ggml-vicuna-13b-1.1-q4_1.bin"
    model_7b = "ggml-vicuna-7b-1.1-q4_0.bin"

    chatbot_13b = Chatbot(bin_path, model_13b)
    chatbot_7b = Chatbot(bin_path, model_7b)

    knowledge_graph_updater = KnowledgeGraphUpdater(chatbot_13b)

    while True:
        activities = run_main_exe(bin_path, model_13b, "What are you doing?", queue)
        insights = run_main_exe(bin_path, model_13b, "What have you learned about what you're doing?", queue)
        general_learnings = run_main_exe(bin_path, model_13b, "What have you learned in general?", queue)

        chatbot_13b_output = queue.get()

        knowledge_graph_updater._update_shortterm_graph(extract_keywords(activities), extract_keywords(insights))

        shortterm_general_learnings = run_main_exe(bin_path, model_7b, "What have you learned in general, given your insight graph?", queue)
        longterm_general_learnings = run_main_exe(bin_path, model_7b, "What have you learned in general, given your general knowledge graph?", queue)

        chatbot_7b_output = queue.get()

        aligned_elements = align_entities(shortterm_general_learnings, longterm_general_learnings)
        knowledge_graph_updater._update_longterm_graph(aligned_elements)

        print(f"Chatbot 13b output: {chatbot_13b_output}")
        print(f"Chatbot 7b output: {chatbot_7b_output}")
