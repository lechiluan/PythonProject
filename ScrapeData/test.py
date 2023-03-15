import spacy
import requests
from bs4 import BeautifulSoup

# Load model
nlp = spacy.load("en_core_web_sm")

# Get URL and extract text
url = "https://www.livescience.com/lidar-maya-civilization-guatemala"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")
text = soup.get_text()
doc = nlp(text)

# Find important sentences
important_sentences = []
for sentence in doc.sents:
    if not sentence.text.isspace():
        if sentence.text.count(".") >= 2:
            important_sentences.append(sentence)
important_sentences = sorted(important_sentences, key=lambda x: x.similarity(doc), reverse=True)

# Generate summary
summary = ""
for i in range(min(10, len(important_sentences))):
    summary += str(important_sentences[i]).strip() + " "
print(summary)
