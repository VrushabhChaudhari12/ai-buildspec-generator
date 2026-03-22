import http.server
import socketserver
import os

PORT = 8765
os.chdir(os.path.dirname(os.path.abspath(__file__)))

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at http://localhost:{PORT}/visualize.html")
    print("Press Ctrl+C to stop.")
    httpd.serve_forever()
