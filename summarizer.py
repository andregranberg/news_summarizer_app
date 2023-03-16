import requests
from newspaper import Article
from transformers import BartTokenizer, BartForConditionalGeneration
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize

tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")

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

if __name__ == '__main__':
    url = input('Enter the URL of the page you want to extract text from: ')
    text = get_article_text(url)
    parts = split_parts(text)

    summarized_parts = []
    for part in parts:
        text = ' '.join(part)
        summary = summarize_text(text)
        summarized_parts.append(summary)

    print("\nComplete Summary:\n")
    for i, summary in enumerate(summarized_parts, 1):
        print(f"{i}. {summary}")
        print()
