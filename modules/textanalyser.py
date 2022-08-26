import re
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import validators
import nltk
import unicodedata
import unidecode
from modules.websiteanalyser import WebsiteAnalyser

wa = WebsiteAnalyser()
        
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
        print(urls)
        urls = [url[0] for url in urls]

        urls = wa.sanitizeurls(urls)

        return urls

    def finddomains(self, string):
        domain_regex = r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]"
        domains = re.findall(domain_regex, string)

        domains = wa.sanitizeurls(domains)

        return domains

    def findemails(self, string):
        email_regex = r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+"
        emails = re.findall(email_regex, string)
        for email in emails:
            try:
                validators.email(email)
            except:
                emails.remove(email)
            
            if email.startswith("n@") or wa.is_valid_tld(email):
                emails.remove(email)

        return [email for email in emails if email != ""]

    def _multireplace(self, string, replace_pattern):
        for arg in replace_pattern:
            string = string.replace(arg[0], arg[1])
        return string

    def _remove_punctuation(self, string):
        replace_pattern = [(v, "") for v in self.punctuation]
        return self._multireplace(string, replace_pattern)

    def findkeywords(self, string):
        string = self._remove_punctuation(string)
        string = self.lemmatizer.lemmatize(string)
        string = word_tokenize(string)

        kwlist = [w for w in string if not w.lower() in self.stopwords and len(w) > 1 and w.isnumeric() == False]
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

        for name in person_list:
            if name[1].lower() in self.stopwords:
                person_list.remove(name)
        return person_list

    def normalize_all(self, text, replace_pynewline=True):
        text = unicodedata.normalize('NFKD', text)
        if replace_pynewline:
            text = text.replace("\n", " ")

        return text

    def parse_direct_chars(self, text):
        parse_chars = [
            ("[at]", "@"),
            ("[dot]", "."),
            (" at ", "@"),
            (" dot ", ".")
        ]

        for char_in, char_out in parse_chars:
            text = text.replace(char_in, char_out)

    def decode_unicode_esc(self, text):
        return str(text)

    def get_hashtags(self, text):
        hashtags = []
        for word in text.split(" "):
            if word.startswith("#"):
                hashtags.append(word[1:])
        
        return hashtags