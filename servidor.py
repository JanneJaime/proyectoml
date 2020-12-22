from flask import Flask, render_template,request
import procesos as p
import json
import requests
from transformers import pipeline, set_seed
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
import re
from nltk.stem.porter import PorterStemmer
app = Flask(__name__)


@app.route('/')
def _():
    if request.values.get('src') != None:
        return render_template('index.html',resp = p.process(request.values.get('src')))
    else:
        return render_template('index.html',resp = p.process())

@app.route('/gpt2')
def _gpt2():
        return render_template('similitud.html')


@app.route('/similitud')
def __():
    return json.dumps(p.similitud(request.values.get('tit'),request.values.get('abst'),request.values.get('topic'))),200,{'Content-Type': 'application/json'}

@app.route('/generar')
def generadorTexto():
    texto = request.values.get('texto')
    generator = pipeline('text-generation', model='gpt2')
    set_seed(42)
    g = generator(texto, max_length=130, num_return_sequences=1)
    g = g[0]['generated_text']
    temp = g
    return json.dumps([ temp, round(jaccard(nlp([g])[0],nlp([texto])[0]),3) ]),200,{'Content-Type': 'application/json'}

def jaccard(texto,generado):
    a=set(texto)
    b=set(generado)
    union=a.union(b)
    inter=a.intersection(b)
    
    if len(union)==0:
        if len(inter)==0:
            return 1
    #similitud
    similitud=len(inter)/len(union)
    return similitud   

def nlp(obj):
    for x,i in enumerate(obj):
        obj[x] = i.lower()
        obj[x] = re.sub('[^A-Za-z0-9]+',' ',i)
        obj[x] = i.split()
        obj[x] = words(obj[x])
        obj[x] = _steamming(obj[x])
    return obj

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



if __name__ == '__main__':
  app.run(host='0.0.0.0',debug=True)   