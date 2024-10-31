from bs4 import BeautifulSoup
import requests
import re
import os

# urls for further uses
base_url = "https://www.vcaa.vic.edu.au"
vce_url = "https://www.vcaa.vic.edu.au/assessment/vce-assessment/past-examinations/Pages/Index.aspx"

# patterns for Regex
pdf_pattern = r'.*\.pdf$'
docx_pattern = r'.*\.docx$'

# request for html
html = requests.get(vce_url).text

# making the soup
soup = BeautifulSoup(html, "lxml")


def get_all_subjects(tag):
    # find <strong> inside <div class="card-header">
    parent = tag.parent  # get the parent label object
    if tag.name == "strong":
        if parent.name == "div" and parent.has_attr("class"):
            if parent["class"][0] == "card-header":
                return tag


# get all subjects and courses
all_subjects = soup.find_all(get_all_subjects)
all_courses = []

# print
while True:
    count = 0
    for subject in all_subjects:
        print(subject.string)
        sibling = subject.parent.find_next_sibling()
        courses = sibling.find_all("a")
        for course in courses:
            print("-*", "[{}]".format(count), course.text)
            all_courses.append(course)
            count += 1
        print()

    print("Enter the number to select a subject:")
    select = int(input())
    new_url = base_url + all_courses[select]["href"]
    print(all_courses[select].text + " course URL: {}".format(new_url))
    # make a new soup
    new_html = requests.get(new_url).text
    new_soup = BeautifulSoup(new_html, "lxml")
    all_links = new_soup.find_all(href=re.compile("^/Documents/exams/"))

    for link in all_links:
        print(link.text, "@", base_url + link["href"])
    print("{} resources found.".format(len(all_links)))
    print("Enter [a] to download all, or any other keys to go back.")

    choice = input()

    if choice != "a":
        continue

    download_folder = "downloads"
    os.makedirs(download_folder, exist_ok=True)  # create one if doesn't exsist

    count = 1  # download index
    for link in all_links:
        # file name
        if re.match(pdf_pattern, link["href"]):
            file_name = link.text + ".pdf"
        elif re.match(docx_pattern, link["href"]):
            file_name = link.text + ".docx"
        else:
            file_name = link.text
        file_name = os.path.join(download_folder, file_name)

        # download status
        print("Downloading {}/{}...".format(count, len(all_links)))

        # get resource
        response = requests.get(base_url + link["href"])

        with open(file_name, "wb") as file:
            file.write(response.content)
        count += 1
    print("Done.")
    input()
