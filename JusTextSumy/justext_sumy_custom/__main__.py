import classifier
import clean_html
import stopword
import summarizer

# parameters
MAX_HEADING_DISTANCE = 150
MAX_GOOD_DISTANCE = 5
LENGTH_LOW = 70
LENGTH_HIGH = 200
STOPWORDS_LOW = 0.2
STOPWORDS_HIGH = 0.3
MAX_LINK_DENSITY = 0.4


def main():
    # load stopwords
    stopwords_path = 'stopwords/English.txt'
    stopwords = stopword.load_stopwords(stopwords_path)

    # fetch and clean HTML content
    # url = input("Enter URL: ")
    url = 'https://practical.engineering/blog/2023/3/21/why-construction-projects-always-go-over-budget'
    html_content = clean_html.fetch_html_content(url)
    html_content = clean_html.clean_html_content(html_content)

    # get text content and segment blocks
    text_content = clean_html.get_text_content(html_content)

    blocks = clean_html.segment_blocks(text_content)

    # classify blocks
    classified_blocks = classifier.classify_blocks(blocks, stopwords, MAX_HEADING_DISTANCE, MAX_GOOD_DISTANCE,
                                                   LENGTH_LOW, LENGTH_HIGH, STOPWORDS_LOW, STOPWORDS_HIGH,
                                                   MAX_LINK_DENSITY)

    # print classified blocks
    for class_label, block in classified_blocks:
        print(f'{class_label}: {block}')

    # save HTML content to file
    with open('html_content.txt', 'w') as f:
        f.write(html_content)

    # save text content to file
    with open('text_content.txt', 'w') as f:
        f.write(text_content)

    # save classified blocks to file
    with open('classified_blocks.txt', 'w') as f:
        for class_label, block in classified_blocks:
            f.write(f'{class_label}: {block}' + '\n')

    # summary_text_content = summarizer.summarize_file_by_line('text_content.txt', 10)
    #
    # with open('summary_text_content.txt', 'w') as f:
    #     f.write(str(summary_text_content))

    summary_text_content = summarizer.summarize_file_by_paragraph('text_content.txt', 10)

    with open('summary_text_content.txt', 'w') as f:
        f.write(str(summary_text_content))


if __name__ == '__main__':
    main()
