from flask import Flask, render_template, request, abort
import requests
import os

app = Flask(__name__)

# Hugging Face Backend URL
HF_BACKEND_URL = os.environ.get("HF_BACKEND_URL", "https://mv09-tech4today.hf.space")

@app.route('/')
def index():
    cat_slug = request.args.get('category', 'top')
    view_mode = request.cookies.get('tech4today_view_mode', 'local')
    
    # Fetch from Hugging Face Intelligence Mesh
    try:
        req_url = f"{HF_BACKEND_URL}/api/mesh-feed?category={cat_slug}&view_mode={view_mode}"
        resp = requests.get(req_url, timeout=10)
        data = resp.json()
    except Exception as e:
        print(f"Error fetching from HF Backend: {e}")
        # Fast fallback payload
        data = {"articles": [], "topics": [], "last_updated": "Offline", "version": "v17 (Proxy Core)"}

    # Radar articles logic identical to original
    raw_list = data.get("articles", [])
    radar_articles = [a for a in raw_list if a.get('category') in ["AI & Coding", "Tools", "Discoveries", "Startup"]][:12]
    
    # Keyword Hotspots
    text_blob = " ".join([a.get('title', '') for a in raw_list])
    words = [w.title() for w in text_blob.split() if len(w) > 5]
    from collections import Counter
    import re
    words = [re.sub(r'[^\w]', '', w) for w in words]
    hotspots = [{"name": word, "count": count} for word, count in Counter(words).most_common(5) if word]

    return render_template(
        'index.html',
        articles=raw_list,
        category_filter=cat_slug,
        topics=data.get('topics', []),
        last_updated=data.get('last_updated', ''),
        version=data.get('version', 'v17'),
        hotspots=hotspots,
        view_mode=view_mode,
        radar_articles=radar_articles
    )

@app.route('/news/<int:news_id>')
def article_detail(news_id):
    try:
        # We need the full mesh to find the article since backend is stateless outside mesh
        req_url = f"{HF_BACKEND_URL}/api/mesh-feed"
        resp = requests.get(req_url, timeout=10)
        data = resp.json()
        articles = data.get("articles", [])
        
        # Searching for the specific pulse string
        # using list comprehension to locate
        article = next((a for a in articles if a.get('id') == news_id), None)
        
        if article:
            return render_template('article.html', article=article)
            
    except Exception as e:
        print(f"Error fetching article detail: {e}")

    return render_template('error.html', title="Pulse Lost", message="This pulse has expired or the backend is offline."), 404

@app.route('/pulse-30')
def pulse_30_deck():
    try:
        req_url = f"{HF_BACKEND_URL}/api/mesh-feed?category=top"
        resp = requests.get(req_url, timeout=10)
        data = resp.json()
        articles = data.get("articles", [])[:15]
    except:
        articles = []

    return render_template('pulse_30.html', articles=articles)

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/legal')
def legal():
    return render_template('legal.html')

if __name__ == '__main__':
    app.run(debug=True, port=3000)
