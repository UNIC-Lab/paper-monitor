import json
import os
import time
from threading import Thread

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

from serpapi import GoogleSearch
def get_citation_num(paper_title) -> int:
    print(paper_title)
    with open('api_pool.json', 'r', encoding="utf-8") as f:
        api_pool = json.load(f)
    for api_key in api_pool:
        params = {
            "engine": "google_scholar",
            "q": paper_title,
            "api_key": api_key,
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        if "error" in results:
            if results["error"] == "Your account has run out of searches.":
                continue
            else:
                raise Exception(results["error"])
        if len(results["organic_results"]) == 0:
            return -1
        else:
            if "cited_by" not in results["organic_results"][0]["inline_links"]:
                return 0
            else:
                return results["organic_results"][0]["inline_links"]["cited_by"]["total"]
    raise Exception("All API keys are used up")

citations_file = 'citations.json'
papers_file = 'papers.json'

# 初始化本地存储的被引次数
if not os.path.exists(citations_file):
    with open(citations_file, 'w', encoding="utf-8") as f:
        json.dump({}, f)

def load_citations():
    with open(citations_file, 'r', encoding="utf-8") as f:
        return json.load(f)

def save_citations(citations):
    with open(citations_file, 'w', encoding="utf-8") as f:
        json.dump(citations, f)

def load_papers():
    with open(papers_file, 'r', encoding="utf-8") as f:
        return json.load(f)

def update_citations(step_time):
    papers = load_papers()
    citations = load_citations()
    for part, papers_list in papers.items():
        for paper in papers_list:
            title = paper['title']
            citations[title] = get_citation_num(title)
            time.sleep(step_time)
    save_citations(citations)

@app.route('/')
def home():
    papers = load_papers()
    citations = load_citations()

    content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Publications</title>
    </head>
    <body>
        <button onclick="updateCitations()">手动更新引用次数</button>
        <script>
            function updateCitations() {
                fetch('/update_citations')
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('引用次数已更新');
                            location.reload();
                        } else {
                            alert('更新失败: '+data.error);
                        }
                    });
            }
        </script>
    """

    for part, papers_list in papers.items():
        content += f"<h1>{part}</h1><ol>"
        for paper in papers_list:
            citation = paper['citation']
            title = paper['title']
            citations_count = citations.get(title, 'N/A')
            content += f'<li>{citation} <span style="color: red;">(被引用次数: {citations_count})</span></li>'
        content += "</ol>"

    content += """
    </body>
    </html>
    """
    
    return render_template_string(content)

@app.route('/update_citations')
def update_citations_route():
    try:
        update_citations(step_time=1)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

def periodic_update(interval):
    while True:
        update_citations(step_time=5)
        time.sleep(interval)

if __name__ == '__main__':
    # 设置定时更新的时间间隔（以秒为单位）
    interval = 3600*24*7  # 每小时更新一次
    thread = Thread(target=periodic_update, args=(interval,))
    thread.daemon = True
    thread.start()
    app.run(host="0.0.0.0")
