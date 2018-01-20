import lxml.etree as ET
import os

file_path = "input/dplp-2017-05-02.xml"
output_folder = 'output/'

# Parses xml file via iterparse and counts number of inproceedings, proceedings and journals
def parsertest():
    inproceedings = 0
    proceedings = 0
    journals = 0

    for event, elem in ET.iterparse(file_path, events=("start", "end"), load_dtd=True):
        if elem.tag == "inproceedings":
            if event == "end" and len(list(elem)) > 0:
                inproceedings += 1
                elem.clear()

        elif elem.tag == "proceedings":
            if event == "end" and len(list(elem)) > 0:
                proceedings += 1
                elem.clear()

        elif event == "start" and elem.tag == "journal":
            journals += 1
            if event == "end" and len(list(elem)) > 0:
                elem.clear()

        else:
            if event == "end" and len(list(elem)) > 0:
                elem.clear()

    print("Inproceedings: " + str(inproceedings))
    print("Proceedings: " + str(proceedings))
    print("Journals: " + str(journals))


# Takes a XML Tag and a number and parses the given number into valid xml
def sample_parser(sample_tag, sample_number, file_name):
    root = ET.Element("dplp")
    baum = ET.ElementTree(root)
    counter = 0
    for event, elem in ET.iterparse(file_path, tag=sample_tag, events=("start", "end"), load_dtd=True):
        if event == "start":
            if (counter < sample_number):
                counter += 1
                parent = ET.SubElement(root, elem.tag, elem.attrib)
                for child in elem:
                    c = ET.SubElement(parent, child.tag, child.attrib)
                    c.text = child.text

        if (counter == sample_number):
            break


    if not os.path.exists(output_folder):
        # creates output folder if it doesnt exist
        os.makedirs(output_folder)
    baum.write(output_folder + file_name)


# Teilaufgabe 1 - 1.)
# parsertest()

# Teilaufgabe 1 - 2.)
# sample_parser("inproceedings", 3, "sample_inproceedings.xml")
# sample_parser("proceedings", 3, "sample_proceedings.xml")

