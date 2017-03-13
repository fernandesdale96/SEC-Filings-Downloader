"""
@author: dayle_fernandes
"""

from bs4 import BeautifulSoup
from selenium import webdriver
from lxml import html
from lxml.etree import tostring
import urllib
import smtplib
import pandas as pd
import os
import errno

#Selenium Chromedriver setup
#Path to the downloaded chrome driver  
chrome_path = r"path/to/chromedriver"
chrome_option =webdriver.ChromeOptions()
#If you wish to change download directory, change the second parameter of following line. Ensure 'r' is added before path for script to work
prefs = {"download.default_directory" : r"default/download/directory"}
chrome_option.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(executable_path=chrome_path,chrome_options=chrome_option)


#Initilization of Array. It will contain all download links along with corresponding date of filing
records = []

#Following module scrapes the SEC website for download links corresponding to filing types
def extract_filing_URL(url):
    driver.get(url)
    r = driver.page_source
    soup = BeautifulSoup(r,"lxml")
    name_div = soup.find_all(class_="companyName")[0]
    name = name_div.find("acronym").previous_sibling
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
            if(cell[0].text_content() == "13F-HR" or cell[0].text_content() == "13F-HR/A"):
                strn = tostring(cell[1])
                date = cell[3].text_content()
                s = BeautifulSoup(strn,"lxml")
                for td in s.find_all("td"):
                    record = []
                    astring = "https://www.sec.gov/" + td.a["href"]
                    record.append(astring)
                    record.append(name)
                    record.append(date)
                    records.append(record)

#Create directories for each company
def set_directories():
    download_path = r"a/download/path"
    df = pd.DataFrame(records)
    names = df[1].unique()
    for name in names:
        #Elimnate escape character from occuring in path.
        name = name.replace("/","")
        new_path = download_path + name.strip()
        if not os.path.exists(new_path):
            try:
                os.makedirs(new_path)
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise
                    

#Following module downloads all all files named and sorted according to company name and date of filing
def file_download(url,cname,date):
    download_path = r"a/download/path"
    driver.get(url)
    src = driver.page_source
    soup_table = BeautifulSoup(src,"lxml")
    link = soup_table.find_all(class_="tableFile")
    string = str(link[0])
    tabl = html.fragment_fromstring(string)
    cname = cname.replace("/","")
    
                                       
   #For relatively newer filings. Table structure changes with older 13F-HR filings on SEC website
    try:
        for row in tabl.iterchildren():
            for cell in row.getchildren()[5]:
                for td in cell.getchildren():
                    strn = tostring(td)
                    s = BeautifulSoup(strn,"lxml")
                    link = "https://www.sec.gov/" + s.a["href"]
                    file_n = cname.strip() + " " + date + ".txt"
                    npath = download_path + cname.strip()
                    #print(npath)
                    file = npath + "/" + file_n
                    #print(file)
                    #Download fle onto corresponding folder
                    urllib.request.urlretrieve(link,file)
    #To download files with older layout. Simple workaround 
    except:
        last_row = link[0].find_all("tr")[-1]
        cols = last_row.find_all("td")
        link_d = "https://www.sec.gov/" + cols[2].find('a').get("href")
        fname = cname.strip() + " " + date + ".txt"
        dpath = download_path + cname.strip()
        file_name = dpath + "/" + fname
        #Download file onto corresponding folder
        urllib.request.urlretrieve(link_d,file_name)
                


#Module to automate url extraction, download and email result of download
def run_download_task():
    for url in URLS:
        extract_filing_URL(url)
    set_directories()
    for rows in records:
        file_download(rows[0],rows[1],rows[2])
    
    #Sends email to desired person when download is complete (Notification of Completion)
    message = "Hi Dayle. Your download is now complete. " + str(len(records)) + " files have been downloaded."
    content = (message)
    mail = smtplib.SMTP('smtp.gmail.com',587)
    mail.ehlo()
    mail.starttls()
    mail.login("a.python.test@gmail.com","aemailpassword")
    mail.sendmail("a.python.test@gmail.com","receiver@emaill.com",content)
    mail.close()
    
    
#Company Search URL
URLS =['https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001037584&type=13F-HR&dateb=&owner=exclude&count=100',
       'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001036250&type=13F-HR&dateb=&owner=exclude&count=100',
       'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001336528&type=13F-HR&dateb=&owner=exclude&count=100',
       'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001166559&type=13F-HR&dateb=&owner=exclude&count=100',
       
       ]

#Calling necessary modules for script to run   
run_download_task()
