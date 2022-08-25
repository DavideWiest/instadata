import re
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import validators
import nltk
import unicodedata
import unidecode


class TextAnalyser:
    def __init__(self, languages=["english", "german"]):
        self.stopwords = []
        for lang in languages:
            for word in stopwords.words(lang):
                self.stopwords.append(word)
        self.punctuation = string.punctuation
        self.lemmatizer = WordNetLemmatizer()

    def findlinks(self, string):
        url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        urls = re.findall(url_regex, string)      
        return [url[0] for url in urls]

    def finddomains(self, string):
        domain_regex = r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]"
        domains = re.findall(domain_regex, string)      
        return [domain for domain in domains if domain != ""]

    def findemails(self, string):
        email_regex = r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+"
        emails = re.findall(email_regex, string)
        for email in emails:
            try:
                validators.email(email)
            except:
                emails.remove(email)

        return [email for email in emails if email != ""]

    def _mutlireplace(self, string, replace_pattern):
        for arg in replace_pattern:
            string = string.replace(arg[0], arg[1])
        return string

    def _remove_punctuation(self, string):
        replace_pattern = [(v, "") for v in self.punctuation]
        return self._mutlireplace(string, replace_pattern)

    def findkeywords(self, string):
        string = self._remove_punctuation(string)
        string = self.lemmatizer.lemmatize(string)
        string = word_tokenize(string)

        kwlist = [w for w in string if not w in self.stopwords]
        return kwlist


    def findnames(self, text):
        person_list = []

        tokens = nltk.tokenize.word_tokenize(text)
        pos = nltk.pos_tag(tokens)
        sentt = nltk.ne_chunk(pos, binary = False)

        for subtree in sentt.subtrees(filter=lambda t: t.label() == 'PERSON'):
            name = []
            person = []

            for leaf in subtree.leaves():
                person.append(leaf[0])
            if len(person) > 1:
                name = [" ".join(person[:-1]), person[-1]]
                if name not in person_list:
                    person_list.append(name)
                
        return person_list

    def unicode_de_escape(self, text):
        return ascii(unicodedata.normalize('NFC', text))
        
    def normalize_all(self, text):
        text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore')
        return unidecode.unidecode(text)