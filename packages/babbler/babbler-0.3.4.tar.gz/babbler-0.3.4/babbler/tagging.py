
import logging
from os.path import dirname, join
from unicodedata import normalize


class Tagger(object):
    """
    Extracts tags from text.
    """

    def __init__(self, scorer, data_path, min_length):
        """
        Load dictionary and stopwords.
        """
        self.scorer = scorer
        self.min_length = min_length
        for wordfile in ("dictionary", "stopwords"):
            path = join(data_path, wordfile + ".txt")
            with open(path) as f:
                setattr(self, wordfile, set([s.strip() for s in f]))

    def possible_for_index(self, words, i):
        """
        Returns up to 4 possible tags - all combinations of the next
        and previous words for the given index. If the word has a
        possessive apostrophe, use the singular form.
        """
        prev = words[i - 1] if i > 0 else None
        prev_valid = prev and prev not in self.stopwords
        next = words[i + 1] if i < len(words) - 1 else None
        next_valid = next and next not in self.stopwords
        word = words[i]
        singular = [word[:len(end) * -1] for end in ("'s", "\xe2\x80\x99s")
                    if word.lower().endswith(end)]
        if singular:
            word = singular[0]
        tags = [word]
        if prev_valid:
            # Combined with previous word.
            tags.append(prev + word)
        if next_valid:
            # Combined with next word.
            tags.append(word + next)
        if prev_valid and next_valid:
            # Combined with previous and next words.
            tags.append(prev + word + next)
        # Remove apostophes.
        return [t.replace("'", "") for t in tags]

    def best_with_score(self, tags):
        """
        Given possible tags, calculates a score for each, and returns
        the highest scoring tag/score pair.
        """
        best = None
        highscore = 0
        for tag in tags:
            score = self.scorer(tag)
            logging.debug("Score for '%s': %s" % (tag, score))
            if score > highscore:
                highscore = score
                best = tag
        return best, highscore

    def tags(self, text, ascii=True):
        """
        Returns tags for the given text.

        Steps:

        1) Go through every word in the text and if non-numeric, valid
           length and non-dictionary, create up to 4 possible tags from
           it, the word combined with the previous word, the next word,
           both previous and next words together, and the word itself.
           Only use previous and next words that aren't stopwords.
        2) Ignore all the possible tags from the word if any of
           them have already been added as tags, eg via the previous
           or next word iteration, or a duplicate word.
        3) Run the score function for each of the tags, and pick the
           highest scoring tag to use from the possibilites for that word.
        4) Sort the chosen tags found for all words by score.

        """
        logging.debug("Getting tags for: %s" % text)
        # Treat dashes and slashes as separators.
        text = unicode(text.replace("-", " ").replace("/", " "))
        # Translate unicode chars to ascii.
        if ascii:
            text = normalize("NFKD", text).encode("ascii", "ignore")
        # Initial list of alphanumeric words.
        words = "".join([c for c in text if c.isalnum() or c in "' "]).split()
        # All tags mapped to scores.
        tags = {}
        for i, word in enumerate(words):
            word = word.replace("'", "")
            # Ignore numbers and numeric positions, eg: '1st' or '44th'.
            numeric = (word.lower().endswith(("st", "nd", "th")) and
                       word[:-2].isdigit()) or word.isdigit()
            too_short = len(word) < self.min_length
            if not (numeric or too_short or word.lower() in self.dictionary):
                possible = self.possible_for_index(words, i)
                logging.debug("Possible tags for the word '%s': %s" %
                              (word, ", ".join(possible)))
                # Check none of the possibilities have been used.
                used = [t.lower() for t in tags.keys()]
                if [t for t in possible if t.lower() in used]:
                    logging.debug("Possible tags already used")
                else:
                    tag, score = self.best_with_score(possible)
                    if tag is not None:
                        logging.debug("Best tag for the word '%s': %s" %
                                      (word, tag))
                        tags[tag] = score
        # Sort tags by score.
        tags = sorted(tags.keys(), key=lambda k: tags[k], reverse=True)
        logging.debug("Tags chosen: %s" % (", ".join(tags) if tags else "None"))
        return tags
