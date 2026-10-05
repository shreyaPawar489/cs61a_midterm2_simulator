"""Run each reference solution against the question's doctests (build-time check)."""
import json, doctest, io, sys, contextlib, signal
PRE = open('prelude.py').read()
exams = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'questions.json'))
setup_over = {}
import re
def docstring(sig):
    m = re.search(r'("""|\'\'\')(.*?)\1', sig, re.S)
    return m.group(2) if m else ''

def run(q, code):
    g = {'__name__': 'exam'}
    exec(PRE, g)
    if q.get('setup'): exec(q['setup'], g)
    if q.get('given'): exec(q['given'], g)
    exec(code, g)
    exs = doctest.DocTestParser().get_examples(q.get('tests_src') or docstring(q['signature']))
    fails = []
    runner = doctest.DocTestRunner(optionflags=doctest.NORMALIZE_WHITESPACE)
    t = doctest.DocTest(exs, g, q['title'], None, 0, None)
    out = io.StringIO()
    r = runner.run(t, out=out.write)
    return r, out.getvalue(), len(exs)
bad = 0
for e in exams:
    for q in e['questions']:
        try:
            signal.alarm(5)
            r, out, n = run(q, q['solution'])
            signal.alarm(0)
            if r.failed or n == 0:
                bad += 1; print('FAIL', e['id'], q['qnum'], q['title'], r, n); print(out[:1500])
        except BaseException as ex:
            signal.alarm(0)
            bad += 1; print('ERR', e['id'], q['qnum'], q['title'], type(ex).__name__, ex)
print('bad', bad)
