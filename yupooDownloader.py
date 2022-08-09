# coding=utf-8

from ctypes.wintypes import PINT
from pydoc import pager
from retrying import retry
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
import csv
import json

with open('details.json')as f:
    data = json.load(f)
for state in data["yupoos"]:
    break

def getAlbumURLS():

    f = open("albumURLs.csv", "w", newline="", encoding="utf-8")
    #os.system("attrib +h albumURLs.csv")
    writer = csv.writer(f, delimiter=' ', quoting=csv.QUOTE_MINIMAL)

    url = state['yupoo_link']
    text = url

    head, sep, tail = text.partition('x.yupoo.com')
    print("Downloading photos from site: " + head + "x.yupoo.com")

    response = requests.get(url)
    data = response.text
    soup = BeautifulSoup(data, features="lxml") #soup = BeautifulSoup(data, 'lxml')
    writer.writerow(["LINKS"])

    row1 = []
    count=0
    for link in soup.findAll('a', class_='album__main'):
        count=count+1
        q = (link.get('href'))

        row1.append(q)
    print("Found " + str(count) + " albums...")


    for c in range(len(row1)):
        writer.writerow([row1[c]])


    f.close()
    print("File with album URLS located in: " + os.getcwd())
    print("Downloading images...")


@retry(stop_max_attempt_number=5)
def createHandler(X):
    try:
        with open((str(X) + '.csv'), 'w', newline='') as file:
            writer = csv.writer(file, delimiter=',')
            #WINDOWS DIRECTORY READING FROM ORIGINAL REPO
            #df = pd.read_csv(os.getcwd() + "\\bf3_strona.csv", sep=' ')
            #WORKING DIR REF IN UNIX SYSTEMS
            df = pd.read_csv('./albumURLs.csv')
            TEXT = (df['LINKS'][X]) #Links

            url = state['yupoo_link'] 
            text = url
            head, sep, tail = text.partition('x.yupoo.com')
            url = head + "x.yupoo.com" + TEXT
            
            print(url)
            
            response = requests.get(url, timeout=None)
            data = response.content
            soup = BeautifulSoup(data, 'lxml')

            pages = soup.find("form", {"class": "pagination__jumpwrap"})
            nb_pages = int(pages.findChildren()[2].findChildren()[0].get('max')) 
            
            for i in range(nb_pages):
                print('Page = ', i+1)
                response = requests.get(url+'&page='+str(i+1), timeout=None)
                data = response.content
                soup = BeautifulSoup(data, 'lxml')
                title = soup.find_all("h2")[0].get_text()

                # writer.writerow([X])
                writer.writerow([title])

                imgs = soup.find_all("div", {"class": "image__imagewrap"})
                for img in imgs:
                    q = img.findChildren()[0].get('data-src')
                    writer.writerow(['https:' + q])
    except : 
        #print("passing")
        pass


def imageDownloader(x):
    try:
        def create_directory(directory):
            if not os.path.exists('dump/' + directory):
                os.makedirs('dump/' + directory)

        def download_save(url, folder, z):
            try:
                create_directory(folder)
                c = requests.Session()
                c.get('https://photo.yupoo.com/')
                c.headers.update({'referer': 'https://photo.yupoo.com/'})
                res = c.get(url, timeout=None)
                with open(f'./dump/{folder}/'+str(z)+'.jpg', 'wb') as f:
                    f.write(res.content) 
            except:
                pass
        #WINDOWS
        #file = pd.read_csv(os.getcwd() + '\\' + str(x) + "TESTY.csv")
        #UNIX
        file = pd.read_csv('./' + str(x) + ".csv")
        count = 0
        try:
            for col in file.columns:

                for url in file[col].tolist():
                    count += 1
                    if str(url).startswith("http"):
                        download_save(url, col, count)
                        count

                print("Downloaded " + str(count) + " images.")
        except:
            pass
        try:
            #path = (os.getcwd() + '\\' + col)
            path = ('./dump/' + col)

            files = os.listdir(path)
            for index, file in enumerate(files):
                os.rename(os.path.join(path, file), os.path.join(path, ''.join([str(index), '_big.jpg'])))
        except:
            pass

    except:
        pass


getAlbumURLS()

for x in range(int(state['productCount'])):
    createHandler(x)
    imageDownloader(x)
    os.remove(str(x) + '.csv')
