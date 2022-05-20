import json 
from sklearn.feature_extraction import text
from sklearn.svm import SVC
from sklearn.linear_model import SGDClassifier


def train(json_user_name):
    try:
        with open('users.json','r') as json_db:
            json_user = json.load(json_db)[json_user_name]
            for index, title in enumerate(json_user['interesting']):
                if title == '':del json_user['interesting'][index]
            for index, title in enumerate(json_user['not_interesting']):
                if title == '':del json_user['not_interesting'][index]
    
        corpus = []
        y = []
        for i in json_user['interesting']:
            corpus.append(i)
            y.append(1)
        for i in json_user['not_interesting']:
            corpus.append(i)
            y.append(0)
        vectorizer = text.TfidfVectorizer(analyzer="char_wb", 
                ngram_range=(2,3))
        X = vectorizer.fit_transform(corpus)
        clf = SVC(probability=True,max_iter=1000)
        clf.fit(X,y)
        return (clf,vectorizer)
    except:
        print('error to parse json or there is no user data')
        return 0
