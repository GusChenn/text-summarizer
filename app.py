from flask import Flask, request
import spacy
from spacy.lang.pt.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest


def summarize(text, per):
    nlp = spacy.load("pt_core_news_md")
    doc = nlp(text)
    tokens = [token.text for token in doc]
    word_frequencies = {}
    for word in doc:
        if word.text.lower() not in list(STOP_WORDS):
            if word.text.lower() not in punctuation:
                if word.text not in word_frequencies.keys():
                    word_frequencies[word.text] = 1
                else:
                    word_frequencies[word.text] += 1
    max_frequency = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word] / max_frequency

    sentence_tokens = [sent for sent in doc.sents]
    sentence_scores = {}
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sent] += word_frequencies[word.text.lower()]
    computed_select_length = int(len(sentence_tokens) * per)
    select_length = 1 if computed_select_length < 1 else computed_select_length
    summary = nlargest(select_length, sentence_scores, key=sentence_scores.get)
    final_summary = [word.text for word in summary]
    summary = "".join(final_summary)
    return summary


app = Flask(__name__)


@app.get("/summarize")
def fils_programming_languages():
    args = request.args
    text = args.get("text", default="", type=str)
    per = args.get("per", default=1, type=float)

    if not text or not per:
        return {"error": "There was a problem processing your request"}

    return {"programming_languages": summarize(text=text, per=per)}
