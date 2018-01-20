import lxml.etree as ET

file_path = "input/dplp-2017-05-02.xml"

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

    elif elem.tag == "journal":
        if event == "end" and len(list(elem)) > 0:
            journals += 1
            elem.clear()
    else:
        if event == "end" and len(list(elem)) > 0:
            elem.clear()



print("Inproceedings: " + str(inproceedings))
print("Proceedings: " + str(proceedings))
print("Journals: " + str(journals))
