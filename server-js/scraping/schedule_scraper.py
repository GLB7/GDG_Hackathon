import time
import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

#Initialize mongo client and database, refresh by dropping database and recreating for every time script runs
load_dotenv()
uri = os.getenv('MONGODB_URI')
client = MongoClient(uri)
db = client['Apollo']
db.drop_collection('courses')
courses_collection = db['courses']
#courses_collection.insert_one({"name": "test"})

#Set up Selenium web driver
options = Options()
#options.add_argument("--headless")  # hide GUI
#options.add_argument("--window-size=1920,1080")  # set window size to native GUI size
#options.add_argument("start-maximized")

driver = webdriver.Chrome(options=options) 
driver.set_page_load_timeout(200)
try:
    driver.get("https://generalssb-prod.ec.njit.edu/BannerExtensibility/customPage/page/stuRegCrseSched")
except Exception as e:
    print(f"Error loading page:", {e})

time.sleep(10)
#Wait until course data loads
#driver.implicitly_wait(10)
# try:
#     WebDriverWait(driver=driver, timeout=10).until(
#         EC.presence_of_element_located((By.CLASS_NAME, 'table.table.table-bordered.table-condensed.table-hover.sections-table'))
#     )
#     print("element found!")
# except Exception as e:
#     print(f"Error {e}")

#Select rows of the subjects table (each subject is clickable to get new page for that subject)
rows = driver.find_elements(By.CSS_SELECTOR, "tbody#pbid-subjListTable-tb tr")

#Go through each subject and get the course data from each, adding to courses collection
for i, row in enumerate(rows):
    try:
        subject_link = row.find_element(By.CSS_SELECTOR, "span.pb-htable a")
        print(f"Clicking on subject: {subject_link.text}")

        subject_link.click()

        time.sleep(10)

        #driver.implicitly_wait(10)

        # WebDriverWait(driver=driver, timeout=10).until(
        #     EC.presence_of_element_located((By.CLASS_NAME, 'table.table.table-bordered.table-condensed.table-hover.sections-table'))
        # )

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        #print(soup.prettify())

        elements = soup.find_all(['h4', 'table'])
        #print(elements)
        curr_course = None

        course_data = {'course_title':None, 'sections':[]}

        for element in elements:
            if(element.name == 'h4'):
                curr_course = element.get_text(strip=True)
            elif(element.name == 'table' and 'sections-table' in element.get('class', [])):
                print("section table")
                section_data = []
                section_rows = element.find_all('tr')
                print(section_rows)
                for row in section_rows:
                    print(row)
                    columns = row.find_all('td')
                    print(columns)
                    section = {'section': columns[0].get_text(strip=True), 'crn':columns[1].get_text(strip=True), 'days':columns[2].get_text(strip=True), 'times':columns[3].get_text(strip=True), 'location':columns[4].get_text(strip=True), 'status':columns[5].get_text(strip=True), 'max':columns[6].get_text(strip=True), 'now':columns[7].get_text(strip=True), 'instructor':columns[8].get_text(strip=True), 'delivery Mode':columns[9].get_text(strip=True), 'credits':columns[10].get_text(strip=True), 'info':columns[11].get_text(strip=True),'comments':columns[12].get_text(strip=True)}
                    section_data.append(section)
                
                if(section_data):
                    course_data['course_title'] = curr_course
                    course_data['sections'].extend(section_data)
                    courses_collection.insert_one(course_data)

                curr_course = None
                course_data = {'course_title':None, 'sections':[]}
                
    except Exception as e:
        print(f"Error processing row {i} with error {e}")
        continue

    

driver.quit()