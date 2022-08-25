from textanalyser import TextAnalyser

text = u"\u2460\ud835\udfd2\ud835\udc95\ud835\udc89 \ud835\udc79\ud835\udc96\ud835\udc8f\ud835\udc8f\ud835\udc86\ud835\udc93 \ud835\udc7c\ud835\udc91 \ud835\udc74\ud835\udc70\ud835\udc75 \ud835\udc75\ud835\udc73 \ud835\udfd0\ud835\udfce\ud835\udfd0\ud835\udfcf\ud83c\uddf3\ud83c\uddf1\n\ud835\udc0c\ud835\udc22\ud835\udc2c\ud835\udc2d\ud835\udc1e\ud835\udc2b \ud835\udc0f\ud835\udc28\ud835\udc29\ud835\udc2e\ud835\udc25\ud835\udc1a\ud835\udc2b\ud835\udc22\ud835\udc2d\ud835\udc32 \ud835\udfd0\ud835\udfce\ud835\udfd0\ud835\udfcf \ud83c\uddf3\ud83c\uddf1\n\ud83c\uddf3\ud83c\uddf1 \ud835\ude73\ud835\ude9e\ud835\ude9d\ud835\ude8c\ud835\ude91\n\ud83c\udfa4 \ud835\ude79\ud835\ude98\ud835\ude97\ud835\ude90\ud835\ude78\ud835\ude97\ud835\ude7b\ud835\ude8e\ud835\ude95\ud835\udea2\ud835\ude9c\ud835\ude9d\ud835\ude8a\ud835\ude8d\n\ud83d\udc5c \ud835\ude7e\ud835\ude99\ud835\ude8e\ud835\ude9b\ud835\ude8a\ud835\ude9d\ud835\ude92\ud835\ude98\ud835\ude97\ud835\ude8e\ud835\ude8e\ud835\ude95 \ud835\ude8a\ud835\ude9c\ud835\ude9c\ud835\ude92\ud835\ude9c\ud835\ude9d\ud835\ude8e\ud835\ude97\ud835\ude9d \ud835\ude74\ud835\ude7c\ud835\ude76"

ta = TextAnalyser()

result = ta.unicode_de_escape(text)
print(result)