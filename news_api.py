import requests
import feedparser
from newspaper import Article
from transformers import BartTokenizer, BartForConditionalGeneration
import nltk
from nltk.tokenize import sent_tokenize
from flask import Flask, jsonify, request
from flask_cors import CORS

# Import your summarization functions here
from summarizer import get_article_text, split_parts, summarize_text


nltk.download('punkt')

tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")

app = Flask(__name__)
CORS(app)

RSS_URL = "https://feeds.bbci.co.uk/news/world/rss.xml"

def get_articles_from_rss():
    feed = feedparser.parse(RSS_URL)
    articles = [
        {
            "title": entry.title,
            "link": entry.link,
        }
        for entry in feed.entries
    ]
    return articles

articles = get_articles_from_rss()
selected_articles = {}


def get_article_text(url):
    article = Article(url)
    article.download()
    article.parse()
    return article.text


def split_parts(text, max_tokens=1024):
    sentences = sent_tokenize(text)
    parts = []
    current_part = []
    current_tokens = 0

    for sentence in sentences:
        tokens = tokenizer.encode(sentence)
        token_count = len(tokens)

        if current_tokens + token_count > max_tokens:
            parts.append(current_part)
            current_part = [sentence]
            current_tokens = token_count
        else:
            current_part.append(sentence)
            current_tokens += token_count

    if current_part:
        parts.append(current_part)

    return parts


def summarize_text(text):
    inputs = tokenizer.encode(text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(inputs, num_beams=4, max_length=150, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary


@app.route('/api/articles', methods=['GET'])
def get_articles():
    return jsonify(articles)


@app.route('/api/selected', methods=['POST'])
def store_selected_articles():
    global selected_articles
    selected_articles = request.get_json()

    summaries = []
    for article in selected_articles:
        text = get_article_text(article['link'])
        parts = split_parts(text)

        summarized_parts = []
        for part in parts:
            text = ' '.join(part)
            summary = summarize_text(text)
            summarized_parts.append(summary)

        summary_text = "\n".join(summarized_parts)
        summaries.append({'title': article['title'], 'summary': summary_text})

    return jsonify(summaries), 200

@app.route('/api/summarize', methods=['POST'])
def summarize_articles():
    selected_articles = request.get_json()
    summaries = []

    for article in selected_articles:
        text = get_article_text(article['link'])
        parts = split_parts(text)
        summarized_parts = [summarize_text(' '.join(part)) for part in parts]
        summary = ' '.join(summarized_parts)

        summaries.append({
            'title': article['title'],
            'summary': summary
        })

    print("Generated summaries:", summaries)  # Add this line to print summaries
    return jsonify(summaries)


if __name__ == '__main__':
    app.run(debug=True)
