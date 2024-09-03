from textblob import TextBlob
from newspaper import Article
import requests
from datetime import datetime
from matplotlib import pyplot as plt

API_KEY = "RcDAhg9H4YDtsb5c3ImMSzbBwl2HzAAC"
BASE_URL = "https://api.nytimes.com/svc/search/v2/articlesearch.json"

def get_articles(query, total_articles=100, start_date=None, end_date=None):
    all_articles = []
    for page in range((total_articles // 10) + 1):
        params = {
            'q': query,
            'api-key': API_KEY,
            'sort': 'newest',
            'page': page,
            'fl': 'web_url,headline,snippet,abstract,pub_date'
        }
        if start_date:
            params['begin_date'] = start_date.strftime('%Y%m%d')
        if end_date:
            params['end_date'] = end_date.strftime('%Y%m%d')
        
        response = requests.get(BASE_URL, params=params)
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            return []
        data = response.json()
        articles = data['response']['docs']
        all_articles.extend(articles[:total_articles - len(all_articles)])
        if len(all_articles) >= total_articles:
            break
    return all_articles[:total_articles]

def analyze_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        text = article.text
        if not text:
            return None, None
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity
        return text, sentiment
    except Exception as e:
        print(f"Failed to analyze {url}: {e}")
        return None, None

query = input("Search for: ")
start_date_str = input("Start date (YYYY-MM-DD): ")
end_date_str = input("End date (YYYY-MM-DD): ")
    
try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
except ValueError as e:
        print(f"Error parsing dates: {e}")
        start_date = None
        end_date = None
    
articles = get_articles(query, total_articles=50, start_date=start_date, end_date=end_date)

if not articles:
        print("No Articles Found")
else:
        sentiments_dates = []
        for article in articles:
            url = article.get('web_url', '')
            headline = article.get('headline', {}).get('main', '')
            snippet = article.get('snippet', '')
            abstract = article.get('abstract', '')
            pub_date_str = article.get('pub_date', '')

            summary_text = f"{headline}. {snippet}. {abstract}"
            print(f"Analyzing: {summary_text}")
            print(f"URL: {url}")
            print(f"Date: {pub_date_str}")

            _, sentiment = analyze_article(url)
            if sentiment is not None:
                sentiment = sentiment * 100
                print(f"Sentiment: {sentiment}")
            else:
                print(f"Skipping article {url} due to analysis failure.")
                continue
            
            if pub_date_str:
                try:
                    pub_date = datetime.strptime(pub_date_str, '%Y-%m-%dT%H:%M:%S%z')
                    formatted_date = pub_date.strftime('%Y-%m-%d')
                    sentiments_dates.append((formatted_date, sentiment))
                    print(f"Formatted Date: {formatted_date}")
                except ValueError as e:
                    print(f"Failed to parse date '{pub_date_str}': {e}")
            else:
                print("Publication date not available.")
                sentiments_dates.append((None, sentiment))

        sentiments_dates = sorted((d, s) for d, s in sentiments_dates if d)

        dates, sentiments = zip(*sentiments_dates)

        if sentiments:
            print("Sentiments:", sentiments)
            print("Dates:", dates)
            dates = [datetime.strptime(date, '%Y-%m-%d') for date in dates]
        else:
            print("No valid articles found for sentiment analysis.")
        
plt.figure(figsize=(12, 6))
plt.plot(range(len(dates)), sentiments, marker='o', linestyle='-', color='b')
plt.xticks(range(len(dates)), [pub_date.strftime('%Y-%m-%d') for pub_date in dates], rotation=45)
plt.ylabel("Sentiment Value")
plt.xlabel("Date")
plt.title(query.title())
plt.grid(True)
plt.tight_layout()
plt.show()