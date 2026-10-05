"""Local PrairieLearn-style exam simulator for the CS 61A Midterm 2 practice papers.

Usage:  python3 server.py   then open http://localhost:6161
"""
import json
import os
import sys
import threading
import webbrowser
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

import grader
from scope import SCOPE, TOPICS, MAIN_TOPICS

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get('PORT', 6161))
STATE_FILE = os.path.join(HERE, 'state.json')
GUIDES_DIR = os.path.join(HERE, 'study-guides')

EXAMS = json.load(open(os.path.join(HERE, 'exam_data.json')))
QUESTIONS = {q['id']: dict(q, term=e['term'], exam=e['id']) for e in EXAMS for q in e['questions']}
state_lock = threading.Lock()


def public(q):
    """What the student may see before grading: no solution, no hidden answers."""
    return {k: q[k] for k in ['id', 'qnum', 'title', 'term', 'exam', 'note', 'paragraphs', 'provided_text',
                              'given', 'signature', 'n_visible']} | {'n_hidden': len(q['hidden']),
                              'topic': q.get('topic'), 'ed_title': q.get('ed_title')}


def catalog():
    return [{'id': e['id'], 'term': e['term'],
             'questions': [{'id': q['id'], 'qnum': q['qnum'], 'title': q['title'], 'topic': q.get('topic'),
                            'ed_title': q.get('ed_title'), 'blurb': q.get('blurb'), 'part_of': q.get('part_of'), 'ed': q.get('ed'),
                            'size': q['solution'].count('\n') + 1} for q in e['questions']]}
            for e in EXAMS]


def load_state():
    try:
        return json.load(open(STATE_FILE))
    except (OSError, ValueError):
        return {}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send(self, body, ctype='application/json', code=200):
        if not isinstance(body, bytes):
            body = json.dumps(body).encode()
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def body(self):
        return json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))) or b'{}')

    def do_GET(self):
        path = self.path.split('?')[0]
        if path in ('/', '/index.html'):
            return self.send(open(os.path.join(HERE, 'index.html'), 'rb').read(), 'text/html; charset=utf-8')
        if path == '/api/catalog':
            return self.send(catalog())
        if path == '/api/scope':
            return self.send({'topics': TOPICS, 'main_topics': MAIN_TOPICS, 'problems': [{'id': '+'.join(ids), 'topic': t, 'ed_title': title, 'blurb': b}
                                                             for t, title, b, ids in SCOPE]})
        if path.startswith('/api/question/'):
            q = QUESTIONS.get(path.rsplit('/', 1)[1])
            return self.send(public(q)) if q else self.send({'error': 'no such question'}, code=404)
        if path.startswith('/api/solution/'):
            q = QUESTIONS.get(path.rsplit('/', 1)[1])
            return self.send({'solution': q['solution'], 'explanation': q['explanation'],
                              'uses': q['sol_uses'] if q['sol_uses'].startswith('Uses code') else ''})
        if path == '/api/state':
            with state_lock:
                return self.send(load_state())
        if path == '/api/guides':
            os.makedirs(GUIDES_DIR, exist_ok=True)
            return self.send(sorted(f for f in os.listdir(GUIDES_DIR) if not f.startswith('.')))
        if path.startswith('/guides/'):
            name = os.path.basename(path[len('/guides/'):].replace('%20', ' '))
            full = os.path.join(GUIDES_DIR, name)
            if os.path.isfile(full):
                ctype = 'application/pdf' if name.lower().endswith('.pdf') else 'text/html; charset=utf-8' \
                    if name.lower().endswith('.html') else 'application/octet-stream'
                return self.send(open(full, 'rb').read(), ctype)
        self.send({'error': 'not found'}, code=404)

    def do_POST(self):
        path = self.path.split('?')[0]
        if path == '/api/grade':
            data = self.body()
            q = QUESTIONS.get(data.get('id'))
            if not q:
                return self.send({'error': 'no such question'}, code=404)
            return self.send(grader.grade(q, data.get('code', '')))
        if path == '/api/state':
            data = self.body()
            with state_lock:
                tmp = STATE_FILE + '.tmp'
                json.dump(data, open(tmp, 'w'))
                os.replace(tmp, STATE_FILE)
            return self.send({'ok': True})
        self.send({'error': 'not found'}, code=404)


if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
    url = f'http://localhost:{PORT}'
    print(f'CS 61A Midterm 2 simulator running at {url}  (Ctrl+C to stop)')
    if '--no-browser' not in sys.argv:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
