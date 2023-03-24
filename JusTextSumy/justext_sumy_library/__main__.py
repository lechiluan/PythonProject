import requests
import justext
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.tokenizers import Tokenizer
from sumy.utils import get_stop_words


def main():
    # fetch and clean HTML content using Justext
    # url = input("Enter URL: ")
    url = 'https://practical.engineering/blog/2023/3/21/why-construction-projects-always-go-over-budget'
    response = requests.get(url)
    paragraphs = justext.justext(response.content, justext.get_stoplist("English"))

    print('Text Content:')
    # concatenate non-boilerplate paragraphs into text_content
    text_content = ''
    for paragraph in paragraphs:
        if not paragraph.is_boilerplate:
            print(paragraph.text)
            text_content += paragraph.text

    with open('justext_content.txt', 'w') as f:
        f.write(text_content)

    # create plaintext parser from text_content
    parser = PlaintextParser.from_string(text_content, Tokenizer("english"))

    # set summarizer and number of sentences for summary
    summarizer = LsaSummarizer()
    summarizer.stop_words = get_stop_words("english")
    sentences_count = 10

    # generate summary
    summary = summarizer(parser.document, sentences_count)
    print('Summary:')
    # print summary
    for sentence in summary:
        print(sentence)

    with open('justext_summary.txt', 'w') as f:
        for sentence in summary:
            f.write(str(sentence))


if __name__ == '__main__':
    main()
