def classify_blocks(blocks, stopwords, max_heading_distance, max_good_distance, length_low, length_high, stopwords_low,
                    stopwords_high, max_link_density):
    classified_blocks = []
    # classify blocks as good, near-good, bad, or short based on link density, length, and stopwords density
    for i, block in enumerate(blocks):
        block = block.strip()
        if not block:
            continue

        length = len(block)
        link_density = block.count('<a>') / length if length > 0 else 0
        words = block.split()
        num_stopwords = sum([1 for word in words if word.lower() in stopwords])
        stopwords_density = num_stopwords / len(words) if len(words) > 0 else 0

        if link_density > max_link_density:
            classified_blocks.append(('bad', block))
        elif length < length_low:
            if link_density > 0:
                classified_blocks.append(('bad', block))
            else:
                classified_blocks.append(('short', block) )
        else:
            if stopwords_density > stopwords_high:
                if length > length_high:
                    classified_blocks.append(('good', block))
                else:
                    classified_blocks.append(('near-good', block))
            elif stopwords_density > stopwords_low:
                classified_blocks.append(('near-good', block))
            else:
                classified_blocks.append(('bad', block))

    return classified_blocks
