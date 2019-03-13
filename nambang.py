# For crawling purpose
import requests
from bs4 import BeautifulSoup
# For db purpose
import sqlite3
# For text mining purpose
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

def crawl(src):
    global c
    try :
        page = requests.get(src)

        # Mengubah html ke object beautiful soup
        soup = BeautifulSoup(page.content, 'html.parser')

        # get all link on page
        links = soup.findAll(class_='gray button')
        pg = soup.findAll(class_='pag_button')
        numPages = list()
        for i in pg:    numPages.append(i.getText())
        # access on each page
        for each_link in links:
            print ('Proses : %.2f' %((c/150)*100) + '%'); c+=0.2
            src = each_link['href']
            page = requests.get(src)
            soup = BeautifulSoup(page.content, 'html.parser')

            konten = soup.find(class_='items list_style')
            konten = konten.find('li')

            judul = konten.find(class_='title').getText()

            detil = konten.findAll('span')
            penulis = detil[0].getText()[10:]
            dospem1 = detil[1].getText()[21:]
            dospem2 = detil[2].getText()[21:]

            abstracksi = konten.findAll('p')
            absInd = abstracksi[0].getText()
            absEng = abstracksi[1].getText()

            conn.execute("INSERT INTO PAPER \
                            VALUES (?, ?, ?, ?, ?, ?)", (judul, penulis, dospem1, dospem2, absInd, absEng));
        conn.commit()
        src = pg[numPages.index('>')]['href']
        crawl(src)
    except ValueError:
        print('Download selesai')
        
def preprosesing(txt):
    # Menghilangkan Kata tidak penting
    SWfactory = StopWordRemoverFactory()
    stopword = SWfactory.create_stop_word_remover()

    stop = stopword.remove(txt)
    #print (stop)


    #Stemming/Kata dasar
    Sfactory = StemmerFactory()
    stemmer = Sfactory.create_stemmer()

    stem = stemmer.stem(stop)
    return stem

#VSM
def countWord(txt):
    '''
        Fungsi ini digunakan untuk menghitung setiap kata pada satu string
    '''
    d = dict()
    for i  in txt.split():
        if d.get(i) == None:
            d[i] = txt.count(i)
    return d

def add_row_VSM(d):
    '''
        Fungsi ini digunakan untuk membangun VSM
    '''
    #init baris baru
    VSM.append([])
    # memasukkan kata berdasarkan kata yang telah ditemukan sebelumnya
    for i in VSM[0]:
        if d.get(i) == None:
            VSM[-1].append(0)
        else :
            VSM[-1].append(d.pop(i));

    # memasukkan kata baru 
    for i in d:
        VSM[0].append(i)
        for j in range(1, len(VSM)-1):
            VSM[j].insert(-2,0)
        VSM[-1].append(d.get(i))

conn = sqlite3.connect('test.db')
c = 1
src = 'https://pta.trunojoyo.ac.id/c_search/byprod/10/'
choice = input("Update data? Y/N").lower()
if choice == 'y':
    conn.execute('drop table if exists PAPER')
    conn.execute('''CREATE TABLE PAPER
                 (JUDUL          TEXT     NOT NULL,
                 PENULIS         TEXT     NOT NULL,
                 DOSPEM1         TEXT     NOT NULL,
                 DOSPEM2         TEXT     NOT NULL,
                 ABSTRAK_INDO    TEXT     NOT NULL,
                 ABSTRAK_ENG     TEXT     NOT NULL);''')
    crawl(src)
    conn.execute("DELETE FROM paper WHERE ABSTRAK_INDO=''")
    conn.commit()

print("Building VSM...")
cursor = conn.execute("SELECT * from PAPER")
cursor = cursor.fetchall()
cursor = cursor[:10]
pertama = True
for row in cursor:
    txt = row[-2]
    cleaned = preprosesing(txt)
    d = countWord(cleaned)
    if pertama:
        pertama = False
        VSM = list((list(), list()))
        for key in d:
            VSM[0].append(key)
            VSM[1].append(d[key])
    else:
        add_row_VSM(d)
    
with open('bow.csv', mode='w') as tbl:
    tbl_writer = csv.writer(tbl, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for row in VSM:
        tbl_writer.writerow(row)

'''
    A little tips for you dude.
    Bikin VSM pake sklearn. Cek e book dari pak mul, bab 4, bag of word

    yg belum:
    2. bikin TF IDF
    4. minggu depan mungkin bicarain ttg seleksi fitur
    5. Modelling : clustering
    6. Perbaiki Stemmingnya anjir. Di corpus.
    
    Other note:
    Nama penulis dsb belum ditambahkan ke matrix. Tapi itu bisa nanti-nanti.
'''
