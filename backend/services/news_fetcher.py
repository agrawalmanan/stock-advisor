import requests
import os
from utils.cache import get_cache, set_cache


def get_stock_news(symbol: str, company_name: str = "") -> list:
    """
    Fetch recent news for a stock using GNews API
    """
    cache_key = f"news_{symbol}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    api_key = os.getenv("GNEWS_API_KEY")
    if not api_key:
        print("GNews API key not found")
        return []

    # Clean symbol and build query
    clean_symbol = symbol.replace(".NS", "").replace(".BO", "")

    if company_name and company_name != "Unknown":
        short_name = " ".join(company_name.split()[:2])
        query = f"{short_name} stock"
    else:
        query = f"{clean_symbol} stock India"

    url = "https://gnews.io/api/v4/search"
    params = {
        "q": query,
        "lang": "en",
        "max": 6,
        "apikey": api_key
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        
        # Debug print
        print(f"GNews status: {response.status_code}")
        
        data = response.json()

        # Debug print
        print(f"GNews keys in response: {list(data.keys())}")
        print(f"Total articles found: {data.get('totalArticles', 0)}")

        # Check if articles key exists
        if "articles" not in data:
            print(f"No articles key in response: {data}")
            return []

        raw_articles = data["articles"]
        print(f"Raw articles count: {len(raw_articles)}")

        if not raw_articles:
            print("Articles list is empty")
            return []

        articles = []
        for article in raw_articles:
            # Skip articles with no title
            if not article.get("title"):
                continue

            articles.append({
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "url": article.get("url", ""),
                "source": article.get("source", {}).get("name", ""),
                "published_at": article.get("publishedAt", ""),
                "image": article.get("image", "")
            })

        print(f"Parsed articles count: {len(articles)}")

        # Cache for 30 minutes
        set_cache(cache_key, articles, ttl_seconds=1800)
        return articles

    except requests.exceptions.Timeout:
        print(f"GNews timeout for {symbol}")
        return []
    except Exception as e:
        print(f"GNews error for {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return []