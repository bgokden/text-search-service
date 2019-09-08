import tf_embed as embed

import veriservice as vs
import os
import time
import collections
import sys
import json

import spacy

nlp = spacy.load('xx_ent_wiki_sm')

sentencizer = nlp.create_pipe("sentencizer")
nlp.add_pipe(sentencizer)

def getHosts():
    return os.getenv('HOSTS', 'localhost:10000')

class SearchAPI:
    def __init__(self, name, hosts = getHosts()):
        self.name = name
        self.vc = vs.VeriClient(hosts)

    def ready(self):
        return embed.tf_embed_loaded

    def search(self, text, resultLimit = 10, groupLimit = 5, powerOf = 1):
        vec = embed.text2vec(text)
        response = self.vc.getKnnStream(feature=vec, k=resultLimit*10, timestamp=0, timeout=3000, retry = 5)
        labels = {}
        results = {}
        counters = {}
        for feat in response:
            print(feat.distance)
            distance = min(feat.distance + sys.float_info.epsilon, sys.float_info.max)
            power = pow(1/distance, powerOf)
            if feat.grouplabel in results:
               if counters[feat.grouplabel] < groupLimit:
                   results[feat.grouplabel] += power
                   counters[feat.grouplabel] += 1
                   labels[feat.grouplabel][counters[feat.grouplabel]] = feat.label
            else:
               results[feat.grouplabel] = power
               counters[feat.grouplabel] = 1
               labels[feat.grouplabel] = {}
               labels[feat.grouplabel][counters[feat.grouplabel]] = feat.label
        sortedResults = collections.OrderedDict(sorted(results.items(), key=lambda x: x[1], reverse=True))
        counter = 0
        result = []
        for key, value in sortedResults.items() :
            result.append({"data": json.loads(key), "relevance": value, "reasons": labels[key] })
            counter += 1
            if counter >= resultLimit:
                break
        return result


    def autocomlete(self, text, resultLimit = 5, powerOf = 1):
        vec = embed.text2vec(text)
        response = self.vc.getKnnStream(feature=vec, k=resultLimit*10, timestamp=0, timeout=3000, retry = 5)
        counter = 0
        result = []
        labels = []
        for feat in response :
            if feat.label in labels:
                continue
            distance = min(feat.distance + sys.float_info.epsilon, sys.float_info.max)
            power = pow(1/distance, powerOf)
            result.append({"data": feat.label, "relevance": power })
            labels.append(feat.label)
            counter += 1
            if counter >= resultLimit:
                break
        return result


    def insertSentence(self, id, text):
        self.send(id, text)

    def insertParagraph(self, id, text):
        self.sendParagraph(id, text)


    def sendParagraph(self, id, text, waitUntilSuccess = True, limit = 100):
        doc = nlp(text)
        for sentence in doc.sents:
            self.send(id, sentence.text, waitUntilSuccess, limit)

    def send(self, id, text, waitUntilSuccess = True, limit = 100):
        if text is None or text == "":
            return
        if len(text) > 512:
            text_arr = text.split()
            if len(text_arr) > 100:
                text = " ".join(text_arr[:100])
        vec = embed.text2vec(text)
        print(text)
        response = self.vc.insert(feature=vec, label=text, grouplabel=id, timestamp=int(time.time()), sequencelengthone=512, sequencedimone=1)
        code = response.code
        if code == 1:
            print("code", code)
        trialCount = 0
        while waitUntilSuccess and code == 1 and trialCount < limit:
            print("retrying")
            time.sleep(5)
            response = self.vc.insert(feature=vec, label=text, grouplabel=id, timestamp=int(time.time()), sequencelengthone=512, sequencedimone=1)
            code = response.code
            print("code", code)
            trialCount = trialCount + 1
