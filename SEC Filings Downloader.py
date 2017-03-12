"""
@author: dayle_fernandes
"""

from bs4 import BeautifulSoup
from selenium import webdriver
from lxml import html
from lxml.etree import tostring
import urllib

#Manually acquired URL which is a seach query for SEC filings of desired company (In this case Brandes Investment Partners)
#Please change URL to get filing details for your desired company 
URL = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001015079&owner=exclude&count=40&hidefilings=0"

#Selenium Chromedriver setup
#Path to the chrome driver directory
chrome_path = r"path/to/chrome/driver"
chrome_option =webdriver.ChromeOptions()
#If you wish to change download directory, change the second parameter of following line. Ensure 'r' is added before path for script to work
prefs = prefs = {"download.default_directory" : r"path/to/desired/download/directory"}
chrome_option.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(executable_path=chrome_path,chrome_options=chrome_option)

#Initilization of Array. It will contain all download links along with corresponding date of filing
records = []

#Add desired comapny name (All downloaded files will be sorted according to this name)
company = "BRANDES INVESTMENT PARTNERS"

#Following module scrapes the SEC website for download links corresponding to filing types
def extract_filing_URL(url):
    driver.get(url)
    r = driver.page_source
    soup = BeautifulSoup(r,"lxml")
    table = soup.find_all(class_="tableFile2")
    rows = table[0]
    soup_str = str(rows)
    tab = html.fragment_fromstring(soup_str)
           
    #Removing first row of Table
    for row in tab.iterchildren():
        row.remove(row.getchildren()[0])
        
    #Extracting 13F-HR links from table 
    for row in tab.iterchildren():
        for cell in row.iterchildren():
            #Script currently looks for 13F-HR filing type. To modify script, simply change the if condition parameter
            if(cell[0].text_content() == "13F-HR"):
                strn = tostring(cell[1])
                date = cell[3].text_content()
                s = BeautifulSoup(strn,"lxml")
                for td in s.find_all("td"):
                    record = []
                    astring = "https://www.sec.gov/" + td.a["href"]
                    record.append(astring)
                    record.append(date)
                    records.append(record)

#Following module downloads all all files named and sorted according to company name and date of filing
def file_download(url, date, name):
    driver.get(url)
    src = driver.page_source
    soup_table = BeautifulSoup(src,"lxml")
    link = soup_table.find_all(class_="tableFile")
    string = str(link[0])
    tabl = html.fragment_fromstring(string)
    for row in tabl.iterchildren():
        for cell in row.getchildren()[5]:
            for td in cell.getchildren():
                strn = tostring(td)
                s = BeautifulSoup(strn,"lxml")
                link = "https://www.sec.gov/" + s.a["href"]
                file = name + " " + date + ".txt"
                urllib.request.urlretrieve(link,file)
                

#Calling necessary modules for script to run
extract_filing_URL(URL)
for rows in records:
    file_download(rows[0],rows[1],company)

