import lxml.etree as ET
import os
import json
import errno
import csv
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

def add_crossref_to_inproceedings():
    crossrefs = []
    inproceedings = db.filter(Inproceedings, {})

    # Abfragen aller nterschiedlichen crossrefs für umschreiben en masse
    # Proceedings muss nur 55 statt 2000 mal durchsucht werden
    for inproceeding in inproceedings:
        try:
            unique_crossref = inproceeding.crossref
        except AttributeError:
            continue
        if unique_crossref not in crossrefs:
            crossrefs.append(unique_crossref)

    # Überprüfen ob ref existiert
    for unique_crossref in crossrefs:
        try:
            ref_obj = db.get(Proceedings, {'key': unique_crossref})
        except:
            continue
        if not ref_obj:
            continue

        # Wiederholungen in der alle Inproceeding der selben Refernz zugewiesen werden
        for inproceeding in db.filter(Inproceedings, {'crossref': unique_crossref}):
            # Alle Werte des Proceedings werden eingetrage, skip bei Primärschlüssel
            for value in ref_obj:
                if value == "pk":
                    continue
                inproceeding["proc:" + value] = ref_obj[value]
            inproceeding.save()
            db.commit()


# Takes data (list), takes a header-list and a filename, and saves the data into a csv-file
def save_csv(save_data, save_header, filename):
    with open(output_folder + filename, 'w+', encoding='windows-1252') as f:
        writer = csv.DictWriter(f, save_header, delimiter=';', extrasaction='ignore', lineterminator='\n')
        writer.writeheader()
        writer.writerows(save_data)
    print('Datensätze gespeichert!')


# finds all inproceedings of a given editor
def find_data_by_editor(editor):
    results = db.filter(Inproceedings, {})
    result_list = []

    for result in results:
        try:
            if result["proc:editor"] == editor:
                result_list.append(result)
        except:
            continue

        # editors are often saved in a list
        for inproceeding_editor in result["proc:editor"]:
            if inproceeding_editor == editor:
                result_list.append(result)


    return result_list


# finds all inproceedings bigger than a given pagecount
def find_data_by_page_count(pagecount):
    results = db.filter(Inproceedings, {})
    result_list = []

    for result in results:
        try:
            pages = result.pages

            pages = pages.split('-')
            if not len(pages) == 2:
                continue

            count = int(pages[1]) - int(pages[0]) + 1
        except:
            continue


        if count > pagecount:
            result_list.append(result)


    return result_list



# unfinished
def count_author_inps():
    results = db.filter(Inproceedings, {})
    result_list = []

    for result in results:
        try:
            for author in result.author:

                for entry in result_list:
                    if entry["author"] == author:
                        entry["count"] += 1


        except:
            pass


save_header = ['author', 'title', 'pages', 'proc:editor', 'proc:title']

##############################################################################
# Aufgaben Start
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

    add_crossref_to_inproceedings()


# Teilaufgabe 3 - 1.)
def exercise3_1():
    print('Exercise 3.1 starting - please wait')

    data = find_data_by_editor("Michael L. Brodie")
    save_csv(data, save_header, "exercise3_1.csv")


# Teilaufgabe 3 - 2.)
def exercise3_2():
    print('Exercise 3.2 starting - please wait')
    page_data = find_data_by_page_count(10)
    save_csv(page_data, save_header, "exercise3_2.csv")


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
        input("Fortsetzen?")


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


