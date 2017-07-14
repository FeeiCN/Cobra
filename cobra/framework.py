# -*- coding: utf-8 -*-
import os
from log import logger
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


def parseXml(root, frame_data, language_data):
    if len(root) != 0:
        try:
            global frame_name, language_name
            frame_name = root.attrib['name']
            language_name = root.attrib['language']
            frame_data.setdefault(frame_name, [])
        except KeyError, e:
            logger.warning(e.message)
        for child_of_root in root:
            frame_data, language_data = parseXml(child_of_root, frame_data, language_data)
        try:
            language_data.setdefault(language_name, {})
            language_data[language_name].setdefault(frame_name, frame_data[frame_name])
        except KeyError:
            logger.warning(e.message)
        return frame_data, language_data
    else:
        frame_data[frame_name].append(root.attrib['value'])
        return frame_data, language_data

def projectInformation(absolute_path):
    allfiles = []
    if os.path.isdir(absolute_path):
        for root, dirs, filenames in os.walk(absolute_path):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                allfiles.append(filepath)
    if os.path.isfile(absolute_path):
        allfiles.append(absolute_path)
    return allfiles

# frame_data = {'wordpress': ['1.php', 2.php]}
# language_data = {'php': {'wordpress': ['1.php', '2.php']}}
if __name__ == "__main__":
    frame_data = {}
    language_data = {}
    project_data = []
    logger.info("Please input your project's absolute_path:")
    absolute_path = raw_input()
    project_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
    rules_path = os.path.join(project_directory, 'cobra/rules/frameworks.xml')
    tree = ET.ElementTree(file=rules_path)
    root = tree.getroot()
    frame_data, language_data = parseXml(root, frame_data, language_data)
    projects_data = projectInformation(absolute_path)
    frames_name = frame_data.keys()
    for frame_name in frames_name:
        for rule_name in frame_data[frame_name]:
            for project_data in projects_data:
                if rule_name in project_data:
                    logger.info("Find the project's framework may be:" + frame_name)



