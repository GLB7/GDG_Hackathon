import requests
from bs4 import BeautifulSoup
import json
import re

links=['https://catalog.njit.edu/undergraduate/architecture-design/#coursestext','https://catalog.njit.edu/undergraduate/computing-sciences/#coursestext','https://catalog.njit.edu/undergraduate/science-liberal-arts/#coursestext','https://catalog.njit.edu/undergraduate/newark-college-engineering/#coursestext','https://catalog.njit.edu/undergraduate/management/#coursestext']
for link in links:
    request=requests.get(link)
    soup=BeautifulSoup(request.text, "html.parser")
    for course in soup.find_all('div', class_='courseblock'):
        items=course.find_all('p')
        doc={}
        courseTitle=items[0].text.replace(u'\xa0',' ')
        courseTitle=str(courseTitle)
        credits=re.search(r'(\d+)(-(\d+))? credit(s?)',courseTitle).group(1).strip()
        doc['Credits']=credits
        hours=re.search(r'(\d+)(-(\d+))? contact hour(s?)',courseTitle).group(1).strip()
        doc['Hours']=hours
        courseTitle=re.sub(r'((\d+)(-(\d+))?) credit(s?).*', '', courseTitle)
        doc['Code']=courseTitle.strip()
        desc=items[1].text
        desc=str(desc)
        desc=re.sub(r'<a [^>]*>(.*?)<\/a>', r'\1', desc)
        desc=desc.replace(u'\xa0',' ')
        prereq=re.search(r'Prerequisite(s?):(.*?)\.',desc)
        if prereq:
            doc['Prerequisites']=prereq.group(2).strip()
        else:
            doc['Prerequisites']=None

        coreq=re.search(r'^Corequisite(s?):(.*?)\.',desc)
        if coreq:
            doc['Corequisites'] = coreq.group(2).strip()
        else:
            doc['Corequisites']=None
        
        preOrCo=re.search(r'Pre or Corequisite(s?):(.*?)\.',desc)
        if preOrCo:
            doc['Prerequisites or Corequisites'] = preOrCo.group(2).strip()
        else:
            doc['Prerequisites or Corequisites']=None
        desc=re.sub(r'Prerequisite(s?):(.*?)\.', '', desc)
        desc=re.sub(r'(Pre or )?Corequisite(s?):(.*?)\.', '', desc)
        doc['Description']=desc.strip()
        requests.post("http://3.86.34.32:5000/add_class", json=doc)
