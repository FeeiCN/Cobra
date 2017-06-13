import os
from cobra.utils.config import project_directory
import xml.etree.ElementTree as ET


def test_xml():
    path_lang = os.path.join(project_directory, 'rules', 'languages.xml')
    tree = ET.parse(path_lang)
    languages = tree.getroot()
    for lang in languages:
        print(lang.attrib)
        for l in lang:
            print(l.get('value'), l.tag)
    assert False
