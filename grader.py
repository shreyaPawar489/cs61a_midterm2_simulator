"""Grade a submission in a separate Python process with a 5 second limit, like PrairieLearn.

Run as a module by the server: grade(question, code) -> result dict.
The child process reads a JSON job on stdin and writes a JSON report on stdout.
"""
import ast
import contextlib
import doctest
import io
import json
import os
import subprocess
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
PRELUDE = open(os.path.join(HERE, 'prelude.py')).read()
TIME_LIMIT = 5


def split_debug(out):
    """Separate DEBUG: lines (shown to the student) from real output (graded)."""
    debug, kept = [], []
    for line in out.splitlines(keepends=True):
        (debug if line.startswith('DEBUG:') else kept).append(line)
    return ''.join(kept), ''.join(debug)


def run_snippet(src, g):
    """Run statements, then evaluate a final expression like the interactive prompt."""
    tree = ast.parse(src)
    last = tree.body.pop() if tree.body and isinstance(tree.body[-1], ast.Expr) else None
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(tree, '<test>', 'exec'), g)
        if last is not None:
            value = eval(compile(ast.Expression(last.value), '<test>', 'eval'), g)
            if value is not None:
                print(repr(value))
    return buf.getvalue()


def short_tb():
    """Traceback limited to the student's code and the test line (no grader frames)."""
    etype, value, tb = sys.exc_info()
    frames = [f for f in traceback.extract_tb(tb) if f.filename in ('your_code.py', '<test>', '<doctest>')]
    lines = ['Traceback (most recent call last):\n'] + traceback.format_list(frames) if frames else []
    return (''.join(lines) if frames else '') + ''.join(traceback.format_exception_only(etype, value)).rstrip()


def child(job):
    g = {'__name__': '__main__'}
    exec(PRELUDE, g)
    report = {'setup_error': None, 'tests': [], 'debug': ''}
    for label, src in [('setup', job['setup']), ('given', job['given'])]:
        if src:
            exec(src, g)
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(job['code'], 'your_code.py', 'exec'), g)
    except BaseException:
        report['setup_error'] = short_tb()
        report['debug'] = buf.getvalue()
        return report
    report['debug'] = split_debug(buf.getvalue())[1]

    checker = doctest.OutputChecker()
    flags = doctest.NORMALIZE_WHITESPACE
    for t in job['tests']:
        entry = {'name': t['name'], 'hidden': t['hidden'], 'source': t['source'], 'expected': t['want'],
                 'context': t.get('context', [])}
        try:
            got = run_snippet(t['source'], g) if not t.get('doctest') else run_doctest(t['source'], g)
            graded, debug = split_debug(got)
            entry['got'] = graded
            entry['debug'] = debug
            entry['passed'] = checker.check_output(t['want'], graded, flags)
        except BaseException as e:
            if isinstance(e, KeyboardInterrupt):
                raise
            out = getattr(e, '_out', '')
            entry['got'] = short_tb()
            entry['debug'] = split_debug(out)[1] if out else ''
            entry['passed'] = bool(t['want'].startswith('Traceback') and type(e).__name__ in t['want'])
        if t.get('setup_step') and entry['passed']:
            continue  # assignments/imports in a doctest only matter if they fail
        report['tests'].append(entry)
    return report


def run_doctest(src, g):
    """A doctest example: compiled in 'single' mode so bare expressions echo."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(src, '<doctest>', 'single'), g)
    return buf.getvalue()


def build_tests(q):
    """Visible doctests (run in order in one namespace), then hidden tests."""
    tests = []
    n, context = 0, []
    for ex in doctest.DocTestParser().get_examples(q['tests_src']):
        body = ast.parse(ex.source).body
        setup_step = not ex.want and not (len(body) == 1 and isinstance(body[0], ast.Expr))
        n += not setup_step
        tests.append({'name': 'doctest setup' if setup_step else f'doctest {n}', 'hidden': False, 'doctest': True,
                      'setup_step': setup_step, 'source': ex.source.rstrip('\n'), 'want': ex.want,
                      'context': list(context)})
        if setup_step:
            context.append(ex.source.rstrip('\n'))
    for i, h in enumerate(q.get('hidden', [])):
        tests.append({'name': f'hidden test {i + 1}', 'hidden': True, 'source': h['source'], 'want': h['want']})
    return tests


def grade(q, code):
    job = {'setup': q.get('setup', ''), 'given': q.get('given', ''), 'code': code, 'tests': build_tests(q)}
    try:
        proc = subprocess.run([sys.executable, os.path.abspath(__file__), '--child'], input=json.dumps(job),
                              capture_output=True, text=True, timeout=TIME_LIMIT, cwd=HERE)
    except subprocess.TimeoutExpired:
        return {'timeout': True, 'score': 0.0, 'tests': [], 'n_tests': 0}
    try:
        report = json.loads(proc.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return {'crash': (proc.stderr or proc.stdout)[-3000:], 'score': 0.0, 'tests': [], 'n_tests': 0}
    n = sum(not t.get('setup_step') for t in job['tests'])
    passed = sum(t['passed'] for t in report['tests'] if not t['name'] == 'doctest setup')
    report['score'] = passed / n if n and not report['setup_error'] else 0.0
    report['n_tests'] = n
    report['n_passed'] = passed
    return report


if __name__ == '__main__' and sys.argv[1:] == ['--child']:
    sys.setrecursionlimit(5000)
    job = json.loads(sys.stdin.read())
    real_stdout = sys.stdout
    result = child(job)
    real_stdout.write('\n' + json.dumps(result) + '\n')
