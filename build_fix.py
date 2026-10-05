"""Hand repairs on top of the PDF parse: predefined helpers, cross-part dependencies, wrap damage.

Reads questions_raw.json, writes questions.json.
"""
import json
import re

exams = json.load(open('questions_raw.json'))
Q = {(e['id'], q['qnum']): q for e in exams for q in e['questions']}

MAKE_TEST_DICE = '''
def make_test_dice(outcomes):
    """Return a zero-argument dice function that cycles through outcomes."""
    index = 0
    def dice():
        nonlocal index
        outcome = outcomes[index % len(outcomes)]
        index += 1
        return outcome
    return dice
'''

# Helpers the exam says are predefined but never prints.
SETUP = {
    ('fa18', 'Q5(a)'): '''
@dataclass
class Poll:
    name: str
    votes: dict
''',
    ('fa20', 'Q3(a)'): '''
@dataclass
class SparseList:
    n: int
    common: Any
    others: dict

def most_common(s):
    """Return the most common element of non-empty list s (ties: first to appear)."""
    best = s[0]
    for x in s:
        if s.count(x) > s.count(best):
            best = x
    return best
''',
    ('fa22', 'Q3(b)'): MAKE_TEST_DICE,
    ('sp22', 'Q8(d)'): MAKE_TEST_DICE,
    ('sp20', 'Q2(b)'): 'curry2 = lambda f: lambda x: lambda y: f(x, y)\n',
    ('sp21', 'Q6(b)(c)'): '''
@dataclass
class EmissionSource:
    name: str
    emissions: dict
    hours: int = 0

def make_source(name, co2, ch4, n2o, hours=0):
    return EmissionSource(name, {'carbon dioxide': co2, 'methane': ch4, 'nitrous oxide': n2o}, hours)

def source_emissions(source, gas):
    return source.emissions.get(gas, 0) * source.hours
''',
    ('sp22', 'Q8(c)'): '''
@dataclass
class HoopPlayer:
    strategy: Any
    score: int = 0
''',
    ('su22', 'Q5'): '''
def is_prime(n):
    if n < 2:
        return False
    k = 2
    while k * k <= n:
        if n % k == 0:
            return False
        k += 1
    return True
''',
    ('su22', 'Q8(b)'): '''
@dataclass
class Boba:
    name: str
    cost: int
    in_stock: bool
    topping: str

@dataclass
class Coffee:
    name: str
    cost: int
    in_stock: bool
    temp: str = 'hot'
''',
    ('su24', 'Q6'): '''
def safe_compose(f, g):
    if f is None or g is None:
        return None
    return lambda x: f(g(x))
''',
    ('su25', 'Q4(b)'): '''
def reverse(x):
    result = 0
    while x:
        result, x = result * 10 + x % 10, x // 10
    return result
''',
}

# Later parts that use the reference solution of earlier parts.
DEPENDS = {
    ('fa17', 'Q3(b)'): [('fa17', 'Q3(a)')],
    ('fa20', 'Q3(b)'): [('fa20', 'Q3(a)')],
    ('fa20', 'Q3(c)'): [('fa20', 'Q3(a)'), ('fa20', 'Q3(b)')],
    ('fa23', 'Q4(b)(iv)'): [('fa23', 'Q4(b)')],
    ('fa24', 'Q4(c)'): [('fa24', 'Q4(a)'), ('fa24', 'Q4(b)')],
    ('fa24', 'Q4(c) blank (l)'): [('fa24', 'Q4(a)')],
    ('fa24', 'Q5(b)'): [('fa24', 'Q5(a)')],
    ('fa25', 'Q6(b)'): [('fa25', 'Q6(a)')],
    ('sp20', 'Q2(b)'): [('sp20', 'Q2(a)')],
    ('sp24', 'Q4(b)'): [('sp24', 'Q4(a)')],
    ('sp25', 'Q5(d)'): [('sp25', 'Q5(c)')],
    ('su20', 'Q3 (plush)'): [('su20', 'Q3 (microscope)')],
    ('su22', 'Q6(b)'): [('su22', 'Q6(a)')],
    ('su23', 'Q3(c)'): [('su23', 'Q3(a)')],
    ('su25', 'Q3(b)'): [('su25', 'Q3(a)')],
    ('su25', 'Q4(b)'): [('su25', 'Q4(a)')],
}

# PDF wrap damage.
Q['fa14', 'Q5(a)']['solution'] = Q['fa14', 'Q5(a)']['solution'].replace(
    "elements[index] !=", "elements[index] != transition(elements[index - 1])}\n    return [len(elements), starts, transition]") + '''
def get(slinky, index):
    start = index
    while start not in starts(slinky):
        start = start - 1
    value = starts(slinky)[start]
    while start < index:
        value = transition(slinky)(value)
        start = start + 1
    return value'''
Q['fa19', 'Q5(a)']['solution'] = Q['fa19', 'Q5(a)']['solution'].split('\n', 1)[1]
q = Q['su21', 'Q5(b)']
q['given'] = 'initial_seen = lambda x: 0'
q['text'] = [l for l in q['text'] if l != q['given']]
q['signature'] = q['signature'].replace('def make_seen_function(f, msvar):', 'def make_seen_function(f, msvar):\n    """Return a seen function that counts msvar once more than f does."""')
Q['sp22', 'Q3']['signature'] = Q['sp22', 'Q3']['signature'].replace("word='avid',definition", "word='avid', definition")

for key, code in SETUP.items():
    Q[key]['setup'] = code
for (eid, qnum), deps in DEPENDS.items():
    q = Q[eid, qnum]
    parts = [Q[d].get('setup', '') + '\n' + Q[d]['given'] + '\n' + Q[d]['solution'] for d in deps]
    q['setup'] = q.get('setup', '') + '\n' + '\n\n'.join(parts)

def docstring(sig):
    m = re.search(r'("""|\'\'\')(.*?)\1', sig, re.S)
    return m.group(2) if m else ''


for e in exams:
    for q in e['questions']:
        src = '\n\n'.join(docstring(part) for part in re.split(r'\n(?=def |@dataclass|class )', q['signature']))
        # Prose like "Case 2: ..." between examples would be read as expected output.
        src = re.sub(r'\n(\s*)(Case \d+:)', r'\n\n\1\2', src)
        q['tests_src'] = src
        q['setup'] = q.get('setup', '').strip()
        q['id'] = e['id'] + '-' + re.sub(r'[^a-z0-9]+', '-', q['qnum'].lower()).strip('-')

json.dump(exams, open('questions.json', 'w'), indent=1)
print('wrote questions.json')
