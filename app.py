from flask import Flask, request
import spacy
from spacy.lang.pt.stop_words import STOP_WORDS as PT_STOP_WORDS
from spacy.lang.en.stop_words import STOP_WORDS as EN_STOP_WORDS
from string import punctuation
from heapq import nlargest
from typing import TypedDict


class RequestBody(TypedDict):
    text: str
    per: float
    language: str


def summarize(text: str, per: float, language: str) -> str:
    if language not in ["pt", "en"]:
        return "Select a valid language (pt or en)"

    if language == "pt":
        model = "pt_core_news_md"
        stop_words = PT_STOP_WORDS
    else:
        model = "en_core_web_sm"
        stop_words = EN_STOP_WORDS

    nlp = spacy.load(model)
    doc = nlp(text)
    word_frequencies = {}
    for word in doc:
        if word.text.lower() not in list(stop_words):
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
def generate_summary() -> dict[str, str]:
    args: RequestBody = request.json

    try:
        text = args["text"]
        per = float(args["per"])
        language = args["language"]
    except KeyError:
        return {"error": "Missing information in the request body"}

    return {"summary": summarize(text=text, per=per, language=language)}


if __name__ == "__main__":
    from waitress import serve

    serve(app, host="0.0.0.0", port=5000)
