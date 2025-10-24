import re
from collections import Counter
import nltk

# Download required NLTK resources (run only once per environment)
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)  # For new NLTK versions
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('averaged_perceptron_tagger_eng', quiet=True)  # NEW for language-specific tagger

def generate_chat_name(prompt: str) -> str:
    # Tokenize text into words
    words = nltk.word_tokenize(prompt)
    tagged = nltk.pos_tag(words)

    # Extract only nouns (N*) and verbs (V*)
    nouns_verbs = [word for word, pos in tagged if pos.startswith("N") or pos.startswith("V")]
    common = Counter(nouns_verbs).most_common(4)  # find 4 most common words

    # Generate a title by joining them
    title = " ".join([word for word, _ in common]).title()

    return title

