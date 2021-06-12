# dependcies- pip install lxml (fast)- or html.parser (in-built) can be used

import requests
from bs4 import BeautifulSoup
import time
#import numpy
#import pandas
import filetype
from pySmartDL import SmartDL
#import re

# getting the html.


def gettoc(soup):
    table = soup.find(id='chapterMainDiv')
    rows = table.tbody.find_all('a')
    urls = list()
    for each in rows:
        l= each.get('href')
        n= validname(each.string.strip())
        s= each.parent.next_sibling.next_sibling.string.strip()
        s=s.split("-")[0]
        print(s+' : '+n)
        if s.isdigit():
            s=int(s)
        else:
            s=0
        # to take account of romans
        urls.append(dict(serial=s, cname=n, clink=l))
    urls.sort(key=mySort)
    print('Obtained TOC. Total chapters= {}'.format(len(urls)))
    return urls


def mySort(e):
  return e['serial']

def validname(n):
    #remove = r'<>:;"/\|?*,'
    for c in r'<>:;"/\|?*,':
        n= n.replace(c,'-')
    #ns = re.split('<|>|:|"|/|\|?|*|,|-', n)
    n = "".join(c for c in n if c.isalnum() or c in list((' ','-','_'))).rstrip()
    while len(n)>70:
        if n.rfind('-')>10:
            n=n[0:n.rindex('-')]
        else:
            n=n[0:-1]
    # sane file names  <>:"/\|?* to exclude <|>|:|"|/|\|?|*|,|-
    # just to be safe
    return n
    


def directlinks(tocx):
    dl = list()
    f = open(title+".csv", "w")
    for each in tocx:
        l=domain+each['clink']
        i=0
        while i<5:
            try:
                cpage = requests.get(l)
                if cpage.status_code == 200:
                    break
                else:
                    print(cpage.status_code)
            except:
                print('Failed on {}. Attempt {}. waiting for 5sec'.format(l,i))
                i+=1
                time.sleep(5)
        #then,
        try:
            soup = BeautifulSoup(cpage.content, "xml")
            chapterId = soup.find(id='chapterId')['value']
            if each['clink'][1:5] == 'book':
                chapterFileName = soup.find(id='fileNamePrefix')['value']
            else:
                chapterFileName = soup.find(id='chapterCode')['value']
        except:
            print('Skipping! Problem with: '+ each['cname'])
            continue #with next item
        location = domain+"/downloadChapterPdfWithName?chapterId=" + chapterId + "&chapterFileName=" + bookISBN + "_" + chapterFileName+"&captchaValue="+captchaValue
        dl.append([each['cname'],location])
        f.write(each['cname']+","+location+"\n")
        print('Got > '+each['cname'])
    f.close()
    return dl
        

# download pdf
def download(dlist):
    print('Total files to download= {}'.format(len(dlist)))
    for d in dlist:
        local_filename = d[0]+'.pdf'
        dest = "C:\\Downloads\\"+ title +"\\"+local_filename
        obj = SmartDL(d[1], dest, fix_urls=True)
        #obj.wait(raise_exceptions=True)
        print('Downloading... {} >>'.format(dlist.index(d))+d[0])
        try:
            obj.start()
            #confirm pdf --check if this is working
            kind = filetype.guess(obj.get_data(binary=False, bytes=128))
            if kind.mime == 'application/pdf':
                print('PDF validated. ;)')
            else:
                print('ERROR in '+d[0]+' >>> '+d[1])
        except:
            print(obj.get_errors())
    a= input('Finally downloading contents & image?(Y/n)...')
    if a!='n':
        conturl= r'https://www.jaypeebrothers.com/contents/' +bookISBN +'.pdf'
        imgurl= r'https://www.jaypeebrothers.com/Images/highres/B' +bookISBN+'.jpg'
        contdest= "C:\\Downloads\\"+ title +"\\Contents.pdf"
        contobj = SmartDL(conturl, contdest)
        contobj.start()
        imgobj = SmartDL(imgurl, contdest)
        imgobj.start()
        if contobj.isSuccessful():
            print('Finished.')
        else:
            print(obj.get_errors())
        
    

def main():
    #domain = "https://www.jaypeedigital.com"
    
    # user input
    #bookId = input("Enter book Id (js: bookId.value): ")
    #bookIsbn = input("Enter ISBN (js: bookIsbn.value): ")
    #if bookId == '' | bookIsbn == '':
    #    bookId='2120'
    #    bookIsbn='9789351521587'
    #subURL = domain+"/fetchChapters?bookId=" + bookId + '&isbn=' + bookIsbn
    #dfs = pandas.read_html(subURL)
    
    uurl = input("Enter the url: ")
    # url validation
    if uurl=='':
        uurl = "https://www.jaypeedigital.com/book/9789386322876" # default
    
    try:
        page = requests.get(uurl)
        if page.status_code ==200:
            soup = BeautifulSoup(page.content, 'html5lib')
            global title
            title=validname(soup.title.string.split('|')[1].strip())
            global domain
            domain = uurl[0:uurl.index('/',10)]
            global bookISBN
            bookISBN = soup.find(id='isbn')['value']
            global captchaValue
            captchaValue = '70'
            print('Title: '+title+'. ISBN='+bookISBN)
            # start--------
            toc = gettoc(soup)
            a = input("Now visiting links...> ")
            alldls=directlinks(toc)
            # list of all direct download links with names of file.
            a = input("Start downloading...(y/n)?")
            if a == 'y':
                download(alldls)  
    except:
        print('Given link cannot be reached!')


main()

# further toc pages can be downloaded from 
# http://www.jaypeebrothers.com/pgDetails.aspx?cat=s&book_id=9789352702862
# or just 
# http://www.jaypeebrothers.com/pgDetails.aspx?book_id=9789352702862
# or directly
# https://www.jaypeebrothers.com/contents/9789352702862.pdf

      
