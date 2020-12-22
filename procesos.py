
import json
import re
import collections
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
import requests
from nltk.stem.porter import PorterStemmer
import numpy as np
import math
from scipy import spatial


def consulta(query):
    response = requests.get("https://core.ac.uk:443/api-v2/search/"+query+"?page=1&pageSize=50&apiKey=ZiykrETNJ0qWQUHoPs5B81A7Reb26YCM")
    json_reponse = response.json()['data']
    titulos = []
    abstract = []
    autores = []
    topics=[]
    for pub in json_reponse:
        if (pub['_source']['title'] != None and pub['_source']['description'] != None and pub['_source']['authors'] != None and pub['_source']['topics'] != None ):
            titulos.append(pub['_source']['title'])
            abstract.append(pub['_source']['description'])
            autores.append(pub['_source']['authors'])
            topics.append(pub['_source']['topics'])
    return titulos,abstract,autores,topics
    
def process(query="machine learning"):
    titulos,abstract,autores,topics = consulta(query)
    titulostemp = titulos[:]  

    query = query.lower()
    query = re.sub('[^A-Za-z0-9]+',' ',query)
    query = query.split()
    query = words(query)
    query = _steamming(query)

     
    listDic = []
    for x,i in enumerate(titulostemp):
        titulostemp[x] = i.lower()
        titulostemp[x] = re.sub('[^A-Za-z0-9]+',' ',i)
        titulostemp[x] = i.split()
        titulostemp[x] = words(titulostemp[x])
        titulostemp[x] = _steamming(titulostemp[x])
        listDic += titulostemp[x]

    dic_titulo = list(collections.Counter(listDic))
    dic_query = list(collections.Counter(query))
    dic_total = list(collections.Counter(dic_titulo+dic_query))

    bolsaDoc = bolsaP(dic_total,titulostemp)
    bolsaQue = bolsaP(dic_total,[query])
    bolsaDocQue = bolsaP(dic_total,titulostemp+query)   

    #DocQuewtf = _wtf(dic_total,titulostemp+query)
    #DocQueidf = _idf(dic_total,titulostemp+query)
    DocQuettfidf = _tfidf(dic_total,titulostemp+query)
    #print(DocQuettfidf)

    punt = puntuacion(bolsaDoc,bolsaQue,DocQuettfidf)
    punt = np.array(punt[0])
    ordenados = np.argsort(punt)[::-1] 
    
    respuesta = []
    for i in ordenados:
        if punt[i] > 0:
            respuesta.append([titulos[i],abstract[i],autores[i],topics[i], round(punt[i],4)])
    return respuesta
def nlp(obj):
    listDic = []
    for x,i in enumerate(obj):
        obj[x] = i.lower()
        obj[x] = re.sub('[^A-Za-z0-9]+',' ',i)
        obj[x] = i.split()
        obj[x] = words(obj[x])
        obj[x] = _steamming(obj[x])
        listDic += obj[x]
    return listDic,obj

def nlpT(obj):
    listDic = []
    for x,i in enumerate(obj):
        i = i.lower()
        i = re.sub('[^A-Za-z0-9]+',' ',i)
        i = i.split()    
        i = words(i)
        i = _steamming(i)
        listDic +=i
    return listDic

def similitud(titulo,abstract,topic):
    titulos,abstracts,autores,topics = consulta(titulo)
    ttemp = titulos[:]
    tabs = abstracts[:]
    ttop = topics[:]

    _,titulos = nlp(titulos)
    listabstracts,abstracts = nlp(abstracts)
    topics = [nlpT(tp) for tp in topics]
        
    _,titulo = nlp([titulo])
    listabstract,abstract = nlp([abstract])
    topic = nlpT([topic])

    mtitulo = np.array(jacc(titulos,titulo[0]))
    mtopics = np.array(jacc(topics,topic))


    dic_total_abstract = list(collections.Counter(listabstracts+listabstract))
    mabstract = np.array(similitud_coseno(dic_total_abstract,abstracts+abstract))
    
    t,c = mabstract.shape
    mabstract = mabstract[t-1][:t-1]
    mtotal = mtitulo*0.3+mabstract*0.4+mtopics*0.3
    print(mtotal)
    ordenados = np.argsort(mtotal)[::-1] 

    respuesta = []
    for i in ordenados:
        if i <= 5 and i != 0:
            respuesta.append([ttemp[i],tabs[i],autores[i],ttop[i],round(mtotal[i],3)])
    
    return respuesta
    



def similitud_coseno(dic1,ab):
    matriztfidf = _tfidf(dic1,ab)
    matrizcoseno=np.zeros((len(matriztfidf[0]),len(matriztfidf[0])))  
    for w1 in range(len(matriztfidf[0])):
        for y1 in range(len(matriztfidf[0])):
            co=matriztfidf[:][w1]
            co1=matriztfidf[:][y1]
            cosenove=1-spatial.distance.cosine(co, co1)
            matrizcoseno[w1,y1]=cosenove
    return matrizcoseno
#stopword
def words (lista):
    n4 = stopwords.words('english')
    for word in lista:
        if word in n4:
            lista.remove(word)
    return lista

#stemming
def _steamming (li):
    stemmer = PorterStemmer()
    n6=[]
    for i in li:
        n6.append(stemmer.stem(i))
    return n6

#bolsa palabras
def bolsaP(dic1,ab):
    matriztf=np.zeros(shape=(len(dic1),len(ab)))   
    cont=0
    for g in range(len(dic1)):
        for f in range(len(ab)):
            num1=contador(dic1[g], ab[f])
            matriztf[g,f]=num1
    return matriztf
#WTF
def _wtf(dic1,ab):
     #tf       
    matriztf=np.zeros(shape=(len(dic1),len(ab)))   
    cont=0
    for g in range(len(dic1)):
        for f in range(len(ab)):
            num1=contador(dic1[g], ab[f])
            matriztf[g,f]=num1

    matrizwt=np.zeros(shape=(len(dic1),len(ab)))   
    for w in range(len(dic1)):
        for y in range(len(ab)):
            veces=matriztf[w,y]
            peso=pesadotf(veces)
            matrizwt[w,y]=peso
    return matrizwt

def _idf(dic1,ab):
    #idf

    matrizidf=np.zeros(shape=(len(dic1),len(ab)))      

    for w in range(len(dic1)):
        for y in range(len(ab)):
            contar=contador1(dic1[w],ab[y])
            pesoidf=idf(contar, len(ab))
            matrizidf[w,y]=pesoidf
    return matrizidf

#df idf wtf
def _tfidf(dic1,ab):
    #tfidf
    matriztfidf=np.zeros(shape=(len(dic1),len(ab)))   

    for w in range(len(dic1)):
        for y in range(len(ab)):
            conteo=contador(dic1[w],ab[y])
            tfidf=uniontfidf(conteo,len(ab))
            matriztfidf[w,y]=tfidf
    return matriztfidf

#  pesado tf
def pesadotf (valor):
    conta=0
    if valor == 0:
        return 0
    else:
        conta=1+math.log10(valor)
    return conta

#contador de palabras vs docuemnto   
def contador (palabra,texto):
     
   conta=0
   for c in range(len(texto)):
       if palabra == texto[c]:
           conta+=1
   return conta 

#contador de palabras vs docuemnto   
def contador1 (palabra,texto):
     
   conta=0
   for c in range(len(texto)):
       if palabra == texto[c]:
           conta+=1
           break
   return conta 
   
#idf
def idf (tf,Ndoc): 
    va=0
    if tf==0:
        return 0
    else:
        va=math.log10(Ndoc/tf)
    return va

#tf y df
def uniontfidf (tf,Ndoc):
    if tf > 0:
        cal=1+math.log10(tf)
        cal2=math.log10(Ndoc/cal)
        cal3=cal*cal2
    else:
        return 0
    return cal3


def puntuacion (bolsad,bolsaq,tfidf):
    bolsaq = np.array(bolsaq)
    bolsad = np.array(bolsad)
    tempg = []
    for i in range(len(bolsaq[0])): 
        tempq = bolsaq[:,i]
        tempq = tempq > 0
        g = []
        for j in range(len(bolsad[0])):
            tempd = bolsad[:,j]
            tempd = tempd > 0
            t = np.logical_and(tempq,tempd)
            t = np.where(t == True)
            t = t[:][0]
            g.append(calcular(i,j+len(bolsaq[0]),t.tolist(),tfidf))
        tempg.append(g)
    return tempg
###########################################
def calcular(q,d,t,tfidf):
  acum=0
  for j in t:
    acum += tfidf[j][d]
  return acum


#metodo de jaccard
def jacc (objetos,obj):
    matrizjacc = []
    for valor1 in objetos:
        a=set(valor1)
        b=set(obj)
        union=a.union(b)
        inter=a.intersection(b)
            
        if len(union)==0:
            if len(inter)==0:
                return 1
        #similitud 
        similitud=len(inter)/len(union)
        matrizjacc.append(similitud)
    return matrizjacc
        