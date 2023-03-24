from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.tokenizers import Tokenizer
from sumy.utils import get_stop_words


# summarize text line by line
def summarize_file_by_line(file_path, sentences_count):
    summaries = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
    # summarize line by line
    for line in lines:
        parser = PlaintextParser.from_string(line, Tokenizer('english'))
        summarizer = LsaSummarizer()
        summary = summarizer(parser.document, sentences_count)
        summaries.append(summary)
        for sentence in summary:
            print(sentence)

    return summaries


# summarize text by all content
def summarize_file_by_paragraph(file_path, sentences_count):
    # concatenate non-boilerplate paragraphs into text_content
    text_content = ''

    with open(file_path, 'r') as f:
        lines = f.readlines()
    # summarize line by line
    for line in lines:
        text_content += line

    # create plaintext parser from text_content
    parser = PlaintextParser.from_string(text_content, Tokenizer("english"))

    # set summarizer and number of sentences for summary
    summarizer = LsaSummarizer()
    summarizer.stop_words = get_stop_words("english")
    sentences_count = 10

    # generate summary
    summary = summarizer(parser.document, sentences_count)
    # print summary
    print('Summary:')
    for sentence in summary:
        print(sentence)
