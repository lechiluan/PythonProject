def load_stopwords(file_path):
    with open(file_path) as f:
        stopwords = set([line.strip() for line in f])
    return stopwords
