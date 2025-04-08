
from flask import Flask, request, Response, send_file, render_template_string
import time, json, os

app = Flask(__name__)
results = []

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <title>k4_urlv4</title>
    <style>
        body {{
            background-color: black;
            color: #0f0;
            font-family: monospace;
            padding: 20px;
        }}
        #banner {{
            text-align: center;
            font-size: 24px;
            color: #0f0;
            text-shadow: 0 0 5px #0f0;
            margin-bottom: 20px;
        }}
        #terminal {{
            background-color: #111;
            padding: 10px;
            border: 1px solid #0f0;
            height: 300px;
            overflow-y: auto;
            white-space: pre-wrap;
        }}
        #results-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        #results-table th, #results-table td {{
            border: 1px solid #0f0;
            padding: 5px;
        }}
    </style>
</head>
<body>
    <div id="banner">[kader11000] - k4_urlv4 Tool</div>

    <label>Base URLs:</label><br>
    <textarea id="base-url" rows="4" style="width:100%;"></textarea><br>

    <label>Wordlist:</label><br>
    <textarea id="wordlist" rows="4" style="width:100%;"></textarea><br>

    <label>Proxy Mode:</label>
    <select id="proxy-mode">
        <option value="none">None</option>
        <option value="auto">Auto</option>
    </select><br><br>

    <button onclick="start()">Start Guessing</button>
    <button onclick="window.open('/results')">Show Results</button>

    <div id="terminal"></div>

    <script>
        function start() {{
            const base_urls = document.getElementById("base-url").value.split("\n").map(x => x.trim()).filter(Boolean);
            const wordlist = document.getElementById("wordlist").value;
            const proxy_mode = document.getElementById("proxy-mode").value;

            document.getElementById("terminal").textContent = "[kader11000@k4_urlv4]$ Starting URL guessing...\n";

            fetch("/stream", {{
                method: "POST",
                headers: {{ "Content-Type": "application/json" }},
                body: JSON.stringify({{ base_urls, wordlist, proxy_mode }})
            }}).then(response => {{
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                function read() {{
                    reader.read().then(({ done, value }) => {{
                        if (done) return;
                        const chunk = decoder.decode(value, {{ stream: true }});
                        chunk.trim().split("data: ").forEach(line => {{
                            if (line) {{
                                const data = JSON.parse(line);
                                if (data.done) {{
                                    document.getElementById("terminal").textContent += `\nCompleted in ${data.elapsed} seconds`;
                                    return;
                                }}
                                if (data.status === 200) {{
                                    document.getElementById("terminal").textContent += `[+] ${data.url} => ${data.status} [${data.proxy}]\n`;
                                }} else {{
                                    document.getElementById("terminal").textContent += `[-] ${data.url} => ${data.status} [${data.proxy}]\n`;
                                }}
                            }}
                        }});
                        read();
                    }});
                }}
                read();
            }});
        }}
    </script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

def get_proxies(mode):
    return ["proxy1", "proxy2"] if mode == "auto" else []

@app.route("/stream", methods=["POST"])
def stream():
    data = request.json
    base_urls = data.get("base_urls", [])
    wordlist = data.get("wordlist", "").split("\n")
    proxy_mode = data.get("proxy_mode", "none")
    proxies = get_proxies(proxy_mode)
    results.clear()
    start_time = time.time()

    def generate():
        count = 0
        for base_url in base_urls:
            for word in wordlist:
                proxy = proxies[count % len(proxies)] if proxies else "none"
                guessed_url = base_url.replace("{{var1}}", word)
                status = 200 if "admin" in guessed_url else 404
                result = {{
                    "url": guessed_url,
                    "status": status,
                    "proxy": proxy,
                    "base_url": base_url
                }}
                if status == 200:
                    results.append(result)
                count += 1
                time.sleep(0.1)
                yield f"data: {{json.dumps(result)}}\n\n"
        yield f"data: {{json.dumps({{'done': True, 'elapsed': round(time.time() - start_time, 2)}})}}\n\n"

    return Response(generate(), mimetype='text/event-stream')

@app.route("/results")
def view_results():
    html = """
    <html><head><style>
    body {{ background:#111; color:#0f0; font-family:monospace; }}
    table {{ width:100%; border-collapse:collapse; }}
    td,th {{ border:1px solid #0f0; padding:5px; }}
    button {{ margin:10px; padding:5px; }}
    </style></head><body>
    <h2>Results - status 200 only</h2>
    <table><tr><th>Base URL</th><th>Guessed URL</th><th>Status</th><th>Proxy</th></tr>
    """
    for r in results:
        html += f"<tr><td>{{r['base_url']}}</td><td>{{r['url']}}</td><td>{{r['status']}}</td><td>{{r['proxy']}}</td></tr>"
    html += """
    </table><br>
    <button onclick="window.location.href='/download-results'">Download</button>
    <button onclick="window.location.href='/'">Back</button>
    </body></html>
    """
    return html

@app.route("/download-results")
def download_results():
    with open("results_k4_urlv4.html", "w") as f:
        f.write(view_results())
    return send_file("results_k4_urlv4.html", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
