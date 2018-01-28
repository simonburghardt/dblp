import lxml.etree as ET
import os
import json
import errno
from blitzdb import Document, FileBackend


class Inproceedings(Document):
    pass


class Proceedings(Document):
    pass


file_path = "input/dblp-2017-05-02.xml"
output_folder = 'output/'
db = FileBackend("./My-DB")


# Parses xml file via iterparse and counts number of inproceedings, proceedings and journals
def parsertest():
    inproceedings = 0
    proceedings = 0
    journals = 0

    for event, elem in ET.iterparse(file_path, events=("start", "end"), resolve_entities=True,
                                    load_dtd=True, huge_tree=True, encoding='ISO-8859-1'):
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
    for event, elem in ET.iterparse(file_path, tag=sample_tag, events=("start", "end"), huge_tree=True,
                                    load_dtd=True, encoding='ISO-8859-1'):
        if event == "start":
            # creates xml tree structure
            if (counter < sample_number):
                counter += 1
                parent = ET.SubElement(root, elem.tag, elem.attrib)
                for child in elem:
                    c = ET.SubElement(parent, child.tag, child.attrib)
                    c.text = child.text

        if event == "end" and len(list(elem)) > 0:
            elem.clear()
        # breaks the loop when sample number is reached
        if (counter == sample_number):
            break

    # creates output folder if it doesnt exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # saves tree structure into xml file
    baum.write(output_folder + file_name)


# Takes xml by tags (param: sample_tag) and parses into dictionary for a given sample number (param: sample_number)
# returns list of dictionaries
def xml_to_dict(sample_tag, sample_number):
    result = []
    counter = 0
    for event, elem in ET.iterparse(file_path, tag=sample_tag, events=("start", "end"), huge_tree=True,
                                    load_dtd=True, encoding='ISO-8859-1'):
        if event == "start":
            # parses xml data into dictionary
            if counter < sample_number:
                counter += 1
                d={}
                d["key"] = elem.attrib["key"]
                d["mdate"] = elem.attrib["mdate"]
                mylist = []
                for child in elem:
                    # author and editor can be multiple entrys and are safed in a mylist
                    if child.tag == "author" or child.tag == "editor":
                        mylist.append(child.text)
                        d[child.tag] = mylist
                    else:
                        if child.text.isnumeric():
                            d[child.tag] = int(child.text)
                        else:
                            d[child.tag] = child.text
            # appends entry dictionary into result mylist
            result.append(d)
        if event == "end" and len(mylist(elem)) > 0:
            elem.clear()
        # breaks the loop when sample number is reached
        if counter == sample_number:
            break

    return result


def xml_to_dict(sample_tag):
    counter = 0
    for event, elem in ET.iterparse(file_path, tag=sample_tag, events=("start", "end"), load_dtd=True,
                                    huge_tree=True, encoding='ISO-8859-1'):
        if event == "start":
            # parses xml data into dictionary

            counter += 1
            d = {}
            d["key"] = elem.attrib["key"]
            d["mdate"] = elem.attrib["mdate"]
            list = []
            for child in elem:
                # author and editor can be multiple entrys and are safed in a list
                if child.tag == "author" or child.tag == "editor":
                    list.append(child.text)
                    d[child.tag] = list
                else:
                    if child.text.isnumeric():
                        d[child.tag] = int(child.text)
                    else:
                        d[child.tag] = child.text
            # appends entry dictionary into result list
        if event == "end" and len(list(elem)) > 0:
            elem.clear()
    return d


# Takes dictionary (param: parsed_data) and saves in json file (name = param: file_name)
def dict_to_json(parsed_data, file_name):
    if not os.path.exists(output_folder):
        # creates output folder if it doesnt exist
        os.makedirs(output_folder)
    fh = open(output_folder + file_name, mode="w", encoding="utf8")
    json.dump(parsed_data, fh, indent=4)


def inproceeding_to_dict(tag, jahr):

    inproceedings = []

    for event, elem in ET.iterparse(file_path, tag=tag, events=("start", "end"), load_dtd=True, huge_tree=True,
                                    encoding='ISO-8859-1'):
        if event == "start":
            if elem.find("year").text == jahr:
                result = xml_to_dict(elem.tag)
                inproceedings.append(result)

            if event == "end" and len(list(elem)) > 0:
                elem.clear()
                while elem.getprevious() is not None:
                    del elem.getparent()[0]

    return inproceedings


def get_proceedings(file):
    proceedings = []

    for event, elem in ET.iterparse(file_path, events=("start", "end"), load_dtd=True, huge_tree=True,
                                    encoding='ISO-8859-1'):
        if elem.tag == "proceedings":
            proceedings.append(xml_to_dict(elem))

        while elem.getprevious() is not None:
            del elem.getparent()[0]

    return proceedings


def list_to_blitzdb(list, db_class):
    for entry in list:
        inp = db_class(entry["inproceedings"])
        db.save(inp)
    db.commit()


# Teilaufgabe 1 - 1.)
def exercise1_1():

    print('Exercise 1.1 starting - please wait')
    parsertest()


# Teilaufgabe 1 - 2.)
def exercise1_2():
    print('Exercise 1.2 starting - please wait')

    sample_parser("inproceedings", 3, "sample_inproceedings.xml")
    sample_parser("proceedings", 3, "sample_proceedings.xml")


# Teilaufgabe 1 - 3.)
def exercise1_3():
    print('Exercise 1.3 starting - please wait')

    inproc_dict = xml_to_dict("inproceedings", 3)
    dict_to_json(inproc_dict, "sample_inproceedings.json")


# Teilaufgabe 2 - 1.)
def exercise2_1():
    print('Exercise 2.1 starting - please wait')

    #list1 = inproceeding_to_dict("inproceeding", "1980")
    list2 = get_proceedings(file_path)
    #list_to_blitzdb(list1, Inproceedings)
    list_to_blitzdb(list2, Proceedings)


# Teilaufgabe 2 - 2.)
def exercise2_2():
    print('Exercise 2.2 starting - please wait')

    return


# Teilaufgabe 3 - 1.)
def exercise3_1():
    print('Exercise 3.1 starting - please wait')

    return


# Teilaufgabe 3 - 2.)
def exercise3_2():
    print('Exercise 3.2 starting - please wait')

    return


# Teilaufgabe 3 - 1.)
def exercise3_3():
    return


def menu():
    while True:
        user_input = input('\t\t1.1 -> Teilaufgabe 1.1 \n\
        1.2 -> Teilaufgabe 1.2 \n\
        1.3 -> Teilaufgabe 1.3 \n\
        2.1 -> Teilaufgabe 2.1 \n\
        2.2 -> Teilaufgabe 2.2 \n\
        3.1 -> Teilaufgabe 3.1 \n\
        3.2 -> Teilaufgabe 3.2 \n\
        3.3 -> Teilaufgabe 3.3 \n\
        0 -> Programm beenden\n')
        if user_input == '1.1':
            exercise1_1()
        elif user_input == '1.2':
            exercise1_2()
        elif user_input == '1.3':
            exercise1_3()
        elif user_input == '2.1':
            exercise2_1()
        elif user_input == '2.2':
            exercise2_2()
        elif user_input == '3.1':
            exercise3_1()
        elif user_input == '3.2':
            exercise3_2()
        elif user_input == '3.3':
            exercise3_3()
        elif user_input == '0':
            exit()
        else:
            print('Ungügltige Eingabe')


def init():
    folders = ["input", "output", "my-db"]
    for path in folders:
        try:
            os.mkdir(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise


init()
menu()
