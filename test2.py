
from modules.textanalyser import TextAnalyser

ta = TextAnalyser()

result = ta.findemails(" hi@hi.com www.google.com/hiiii www.google.com/adbdcd http://www.google.com/search https://www.google.com https://google.com http://google.com")

print(result)
