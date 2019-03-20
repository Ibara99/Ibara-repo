from random import randrange
import numpy as np
data = np.array([[1, 3],
        [3, 3],
        [4, 3],
        [5, 3],
        [1, 2],
        [4, 2],
        [1, 1],
        [2, 1]])

c = 3  #jumlah cluster
maxIter = 100
w = 2
epsilon = 0.000001 #eror

# keanggotaan awal, random dengan syarat total =1
keanggotaan = []
for baris in range (len(data)):
    tmpBaris=[]; i = 0; coba=0
    while i < c:
        if i == c-1:
            tmp = float('%.2f'%(1-sum(tmpBaris)))
        else:
            tmp = randrange(1,100)/100
            while sum(tmpBaris)+tmp > 1:
                if coba > 5:
                    tmpBaris=[]; coba=0; i=0
                tmp = randrange(1,100)/100; coba += 1
        tmpBaris.append(tmp); i += 1
    keanggotaan.append(tmpBaris)
keanggotaan=np.array(keanggotaan)

keanggotaan = np.array([[0.3,	0.3,	0.4],
[0.3,0.5,	0.2],
[0.8,0.1,	0.1],
[0.5,0.2,	0.3],
[0.5,0.1,	0.4],
[0.2,0.1,	0.7],
[0.3,0.4,	0.3],
[0.6,0.2, 0.2]])

miuKuadrat = np.round(keanggotaan ** w, 2)
sumMiuKuadrat = []
for i in range(c):
    sumMiuKuadrat.append(sum(miuKuadrat[:,i]))
sumMiuKuadrat = np.round_(sumMiuKuadrat,2)

sumMKX=[]
for i in range(c):    
    tmp =np.reshape(miuKuadrat[:,i], (len(miuKuadrat),1))
    mkX = data*tmp
    
    tmp = []
    for j in range(len(mkX[0])):
        tmp.append(sum(mkX[:,j]))
    sumMKX.append(tmp)
sumMKX = np.array(sumMKX)

pusatCluster = sumMKX/sumMiuKuadrat.reshape(c,1)

X_V = []
tmp = []
for baris in range(len(data)):
    total = 0
    for clus in range(len(pusatCluster)):
        tot = 0
        for col in range(len(pusatCluster[0])):
            tot += (data[baris, col]-pusatCluster[clus, col])**2
        total += tot
    print(total)
        
    '''tmp = data[:,i].reshape(len(data),1)
    print((tmp - pusatCluster[0,i])**2)
    try :
        tmp1 +=(tmp - pusatCluster[0,i])**2
    except:
        tmp1 =(tmp - pusatCluster[0,i])**2
    X_V.append(tmp1)

tmp=[]
for i in range(len(X_V[0])):
    tampung=[]
    for col in X_V:
        tampung.append(col[i,0])
    tmp.append(tampung)
X_V = np.array(tmp)
'''
L = X_V * miuKuadrat

totalL = []
for i in L:
    totalL.append(sum(i))
totalL = np.array(totalL)

f_objektive = sum(totalL)

LT = X_V ** (-1/(w-1))

totalLT = []
for i in LT:
    totalLT.append(sum(i))
totalLT = np.array(totalLT)
