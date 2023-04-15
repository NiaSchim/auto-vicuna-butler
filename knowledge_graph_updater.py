import os
import threading
import time
from xml.etree import ElementTree as ET
import sys
import response_generator


script_dir = os.path.dirname(os.path.abspath(__file__))

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

            activities = response_generator.get_response(os.path.join(script_dir, self.model_13b), "What are you doing?")
            insights = response_generator.get_response(os.path.join(script_dir, self.model_13b), "What have you learned about what you're doing?")
            general_learnings = response_generator.get_response(os.path.join(script_dir, self.model_13b), "What have you learned in general?")

            self._update_shortterm_graph(extract_keywords(activities), extract_keywords(insights))

            shortterm_general_learnings = response_generator.get_response(os.path.join(script_dir, self.model_7b), "What have you learned in general, given your insight graph?")
            longterm_general_learnings = response_generator.get_response(os.path.join(script_dir, self.model_7b), "What have you learned in general, given your general knowledge graph?")

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


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    bin_path = os.path.dirname(os.path.abspath(__file__))
    model_13b = "ggml-vicuna-13b-1.1-q4_1.bin"
    model_7b = "ggml-vicuna-7b-1.1-q4_0.bin"

    knowledge_graph_updater = KnowledgeGraphUpdater(bin_path, model_13b, model_7b)

    while True:
        activities = response_generator.get_response(os.path.join(script_dir, model_13b), "What are you doing?")
        insights = response_generator.get_response(os.path.join(script_dir, model_13b), "What have you learned about what you're doing?")
        general_learnings = response_generator.get_response(os.path.join(script_dir, model_13b), "What have you learned in general?")

        knowledge_graph_updater._update_shortterm_graph(extract_keywords(activities), extract_keywords(insights))

        shortterm_general_learnings = response_generator.get_response(os.path.join(script_dir, model_7b), "What have you learned in general, given your insight graph?")
        longterm_general_learnings = response_generator.get_response(os.path.join(script_dir, model_7b), "What have you learned in general, given your general knowledge graph?")

        aligned_elements = align_entities(shortterm_general_learnings, longterm_general_learnings)
        knowledge_graph_updater._update_longterm_graph(aligned_elements)

        print(f"Chatbot 13b output: {general_learnings}")
        print(f"Chatbot 7b output: {longterm_general_learnings}")
