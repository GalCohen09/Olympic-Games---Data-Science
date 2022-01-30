from os import error
from time import sleep
from bs4 import BeautifulSoup
from numpy import string_
import numpy
import requests
import pandas as pd

cols={"season","compettion_year", "city", "event", "compettor", "pos", "medal","sex", "noc", "year of birth","age", "cm", "kg"}
df=pd.DataFrame(columns=cols)
    
    
def main():
    createCsv()
    df.to_csv("res.csv")

   
domain = "http://www.olympedia.org"
    
def createCsv():
    url = "http://www.olympedia.org/editions/results"
    response = requests.get(url)
    
    soup = BeautifulSoup(response.content, "html.parser")
    container = soup.find("div", attrs={"class": "container"})
    tables = container.findAll("table", attrs={"class": "table table-striped"})
    summerOlympic = tables[0]
    try:    
        findCompettionNameAndLink(summerOlympic, "summer")
    except Exception as e:
        print(e)

# first page
def findCompettionNameAndLink(olympicType, season):
    #  trs of all the olympics
    trs = olympicType.findAll("tr")
    # we only intrested in olympics from 1960 
    for i in range(13,len(trs)):
        td = trs[i].find("td")
        # spliting the compettion name into the city and year 
        str1 = " "
        city = str1.join(td.text.split()[0:len(td.text.split()) -1])
        compettionYear = td.text.split()[len(td.text.split())-1]
        # link to the detailes of the compettion and it's participents
        link = domain + td.find("a")['href']
        try:    
            getEvent(link, season, city, compettionYear)
        except Exception as e:
            print(e)
        

# second page
def getEvent(link, season, city, compettionYear):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, "html.parser")
    container = soup.find("div", attrs={"class": "container"})
    table = container.find("table", attrs={"class": "table"})
    # the trs with the detailes of the participents are divided to even and odd classes
    # and there is a tr with the type of event (type of sport), that is of no intrest to us so we ignore it
    trs = table.findAll("tr", attrs={"class": "even"})
    for tr in trs: 
        a = tr.find("td").a
        eventName = a.text
        link = domain + a['href']
        try:    
            getEventDeatails(link, season, city, eventName, compettionYear)
            global df
            df.to_csv("res.csv")
            sleep(2)
        except Exception as e:
            print(e)
    trs = table.findAll("tr", attrs={"class": "odd"})
    for tr in trs: 
        a = tr.find("td").a
        eventName = a.text
        link = domain + a['href']
        try:    
            getEventDeatails(link, season, city, eventName, compettionYear)
            df.to_csv("res.csv")
            sleep(2)
        except Exception as e:
            print(e)

            
# third page
# get the detailes of the event
def getEventDeatails(link, season, city, eventName,compettionYear):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, "html.parser")
    container = soup.find("div", attrs={"class": "container"})
    table = container.find("table", attrs={"class": "table table-striped"})
    # each row contain the info of a single participent
    trs = table.findAll("tr")
    numOfCols = len(trs[0].findAll("th"))
    print("numOfCols: ", numOfCols, " ,city: ", 
          city, " ,compettionYear: ", compettionYear,
          " ,eventName: " , eventName)
    
    if len(trs) > 0:
        # because each table has a diffrent layout we need to decide in each table what is the index of participent name 

       posOfCompetitorName = findIndexOfCDetails(trs[0])
       print("posOfCompetitorName: ", posOfCompetitorName)
       for tr in trs:
          tds = tr.findAll("td")
          if tds:
              a = tds[posOfCompetitorName].find("a")
              pos = tds[0].text
              if a:
                  compettorLink = domain + a['href']
                  compettorName = a.text

                  if pos == "1" or pos == "=1":
                    medal = "Gold"
                  elif  pos == "2" or pos == "=2":
                      medal = "Silver"
                  elif  pos == "3" or pos == "=3":
                      medal = "Bronze"
                  else:
                      medal = numpy.nan
                  try:    
                    getCompettorData(compettorLink, season, city, eventName, compettorName, pos, medal,compettionYear)

                  except Exception as e:
                    print(e)


def findIndexOfCDetails(tr):
    ths = tr.findAll("th")
    indexOfName = 0
    CompetatorOptions = ["Competitor(s)","Player","Athlete", "Swimmer","Judoka", "Gymnast", "Archer","Fighter","Lifter",
                         "Boxer", "Shooter", "Triathlete", "Boat","Surfer","Climber",
                         "Skater","Pentathlete","Karateka","Fencers","Diver","Cyclist",
                         "Wrestler","Rider"]
    for i in range(0,len(ths)):
        if ths[i].text in  CompetatorOptions:
            return i    
    return numpy.nan

# gets the data of a single participent and add the data to the datafreame
def getCompettorData(link, season, city, eventName, compettorName, pos, medal,compettionYear):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, "html.parser")
    container = soup.find("div", attrs={"class": "container"})
    table = container.find("table",attrs={"class":"biodata"})
    # personal information like sex, name, etc.
    trs = table.findAll("tr")
    # for unknown values
    sex = numpy.nan
    noc = numpy.nan
    cm = numpy.nan
    kg = numpy.nan
    yearOfBirth =numpy.nan
    age = numpy.nan
    # find the personal detailes if exists
    for tr in trs:
        if tr.find("th").text == "Sex":
            sex = tr.find("td").text
        if tr.find("th").text == "NOC":
            noc = tr.find("td").text[1:]
        if tr.find("th").text == "Measurements":
            measurements = tr.find("td").text
            if "/" in measurements:
                cm = measurements.split("/")[0].split()[0]
                kg = measurements.split("/")[1].split()[0].split("-")[0]
        if tr.find("th").text == "Born":
            date = tr.find("td").text.split()[:3]
            if str.isdigit(date[len(date)-1]):
                yearOfBirth = date[len(date)-1]
                age = int(compettionYear) - int(yearOfBirth)
    
    # save the entry to the datafreame
    newEntry = {'season': [season],'city': [city], 'compettion_year': [compettionYear],
    'event': [eventName], 'compettor': [compettorName],'pos': [pos],
    'medal': [medal], 'sex': [sex],'noc': [noc], 'year of birth': [yearOfBirth],
    'age': [age], 'cm': [cm], 'kg': [kg]}
    dataFrame2 = pd.DataFrame(newEntry,columns=cols)
    global df
    df = df.append(dataFrame2)
      
if __name__ == "__main__":
    
    main()