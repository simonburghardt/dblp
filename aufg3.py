from blitzdb import Document
from blitzdb import FileBackend
import csv

backend = FileBackend("my-db")
output_folder = 'output/'

class inproceedings(Document):
    pass


# Takes data (list), takes a header-list and a filename, and saves the data into a csv-file
def save_csv(save_data, save_header, filename):
    with open(output_folder + filename, 'w+', encoding='windows-1252') as f:
        writer = csv.DictWriter(f, save_header, delimiter=';', extrasaction='ignore', lineterminator='\n')
        writer.writeheader()
        writer.writerows(save_data)
    print('Datensätze gespeichert!')


# finds all inproceedings of a given editor
def find_data_by_editor(editor):

    results = backend.filter(inproceedings, {})
    result_list = []

    for result in results:
        try:
            if (result["proc:editor"] == editor):
                result_list.append(result)

            # editors are often saved in a list
            for edt in result["proc:editor"]:
                if edt == editor:
                    result_list.append(result)

        except:
            pass
            # print("something didnt wurk")

    return result_list


# finds all inproceedings bigger than a given pagecount
def find_data_by_page_count(pagecount):

    results = backend.filter(inproceedings, {})
    result_list = []

    for result in results:
        try:
            pages = result.pages
            pages = pages.split('-')

            count = int(pages[1]) - int(pages[0]) + 1

            if (count > pagecount):
                result_list.append(result)

        except:
            pass

    return result_list


# counts for every author on how many inproceedings he is mentiones
def count_author_inps():

    results = backend.filter(inproceedings, {})
    result_list = []

    for result in results:
        try:
            for author in result.author:
                # checks if author is already in result_list
                for ath in result_list:
                    if ath["author"] == author:
                        ath["count"] += 1
                        break

                else:
                    result_list.append({"author": author, "count": 1})

        except:
            pass

    # sorts the list, most counts on top
    result_list = sorted(result_list, key=lambda k: k['count'], reverse=True)
    return result_list



save_header = ['author', 'title', 'pages', 'proc:editor', 'proc:title']

# Aufgabe 3 - 1.)
# data = find_data_by_editor("Michael L. Brodie")
# save_csv(data, save_header, "michael_brodie.csv")

# Aufgabe 3 - 2.)
# page_data = find_data_by_page_count(10)
# save_csv(page_data, save_header, "morethan10pages.csv")

# Aufgabe 3 - 3.)
# count_data = count_author_inps()
# save_csv(count_data, ['author', 'count'], "author_count_sss.csv")
