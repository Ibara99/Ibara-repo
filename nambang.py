import requests
from bs4 import BeautifulSoup
import sqlite3

def crawl (src):
    '''
        Function ini berguna untuk web crawling
        src = (string) berupa url web yang akan di crawl
    '''
    # Download html dari web
    print('Downloading page...')
    page = requests.get(src)

    # Mengubah html ke object beautiful soup
    soup = BeautifulSoup(page.content, 'html.parser')

    # Menyempitkan area pencarian, agar lebih akurat.
    content = soup.find(class_='soft-gray-content')

    # Mengambil semua barang yang dijual
    producs = content.findAll(class_='col-md-6 col-sm-6')

    #lalu diekstrak satu per satu
    for buku in producs:
        judul = list(buku.find(class_='product-name').children)[1].getText()

        # Cek apakah buku tsb memiliki keterangan (penulis, kategori) atau tidak, 
        keterangan = buku.find(class_='text-muted')
        if keterangan != None:
            links = keterangan.findAll('a')
            pengarang = links[0].getText()
            kategori = links[1].getText()
        else :
            pengarang = kategori = ''
        
        harga = buku.find(class_='product-price').getText()

        # Insert hasil crawl ke dalam database SQLite
        conn.execute("INSERT INTO BUKU \
                    VALUES ('%s', '%s', '%s', '%s')" %(judul, pengarang, kategori, harga));

    # Cek apakah ada page selanjutnya, jika ada maka lakukan rekursi
    pagination = content.find(class_='pagination')
    pages = pagination.findAll('a')
    # cek tombol terakhir,
    #jika tombol terakhir adalah next, link yang diambil dari tombol terakhir
    if pages[-1].has_attr('rel'):
        src = pages[-1]['href']
        crawl(src)
    #jika tombol next ada di ke dua dari kanan, link yang diambil dari tombol tsb
    # Karena bisa aja tombol terakhir berupa <last page>
    elif pages[-2].has_attr('rel') :
        src = pages[-2]['href']
        crawl(src)
    #jika tidak ada tombol next maka rekursi selesai

#-------------------------------------
# MAIN PROGRAM
#-------------------------------------

#Deklarasi SQLite
conn = sqlite3.connect('test.db')
choice = input("Apakah Anda ingin menggunakan data sebelumnya? Y/T").upper()
if choice != "Y":
    conn.execute('drop table if exists BUKU')
    conn.execute('''CREATE TABLE BUKU
             (JUDUL          TEXT     NOT NULL,
             PENGARANG       TEXT     NOT NULL,
             KATEGORI        TEXT     NOT NULL,
             HARGA           TEXT     NOT NULL);''')

    # Deklarasi URL Web
    #src = "http://bukurepublika.id/page/detail/58/Best-Seller"
    src = 'http://bukurepublika.id/page/detail/59/Terbaru'

    crawl(src)
    conn.commit()


# Tes isi dari database
choice = input("Tampilkan data? Y/N").upper()
if choice != "Y":
    cursor = conn.execute("SELECT * from BUKU")
    h = ('Judul', 'pengarang', 'kategori', 'harga')
    print(h)
    for row in cursor:
        print(row)

#--------------#
#    update    #
#--------------#

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

def preprosesing(txt):
    # Menghilangkan Kata tidak penting
    SWfactory = StopWordRemoverFactory()
    stopword = SWfactory.create_stop_word_remover()

    stop = stopword.remove(txt)
    print (stop)


    #Stemming/Kata dasar
    Sfactory = StemmerFactory()
    stemmer = Sfactory.create_stemmer()

    stem = stemmer.stem(stop)
    return stem

#VSM
def countWord(txt):
    d = dict()
    for i  in txt.split():
        if d.get(i) == None:
            d[i] = txt.count(i)
    return d

def add_row_VSM(d):
    VSM.append([])
    for i in VSM[0]:
        if d.get(i) == None:
            VSM[-1].append(0)
        else :
            VSM[-1].append(d.pop(i));
		
    for i in d:
        VSM[0].append(i)
        for j in range(1, len(VSM)-1):
            VSM[j].append(0)
        VSM[-1].append(d.get(i))

cursor = conn.execute("SELECT * from BUKU")
pertama = True
for row in cursor:
    txt = row[0]
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

