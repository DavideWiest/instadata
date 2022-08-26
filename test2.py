
from modules.textanalyser import TextAnalyser

ta = TextAnalyser()

result = ta.findlinks("www.google.com google.com http://www.google.com https://www.google.com https://google.com http://google.com")

print(result)
