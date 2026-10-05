"""Parse extracted exam/solution text into questions_raw.json (one-time build step)."""
import json, re, glob, os, sys
TXT = sys.argv[1]
HDR = re.compile(r'^\s*(Q[0-9].*?)\s{2,}(.+?) (?:Fall|Spring|Summer) (\d{4}) (?:MT2|Midterm)')
PAGE = re.compile(r'^CS 61A .* · page \d+ of \d+$')

def lines_of(path):
    out = []
    for l in open(path).read().split('\n'):
        if l == '=====PAGE=====' or PAGE.match(l):
            continue
        out.append(l.rstrip())
    return out

def split_sections(lines):
    secs, cur = [], None
    for l in lines:
        m = HDR.match(l)
        if m:
            cur = {'qnum': m.group(1), 'title': m.group(2).strip(), 'header': l, 'body': []}
            secs.append(cur)
        elif cur is not None:
            if l.startswith('Reference: linked lists'):
                cur = None
                continue
            cur['body'].append(l)
    return secs

def is_code(l):
    return bool(re.match(r'^(def |class |@|\s|from |import |[A-Za-z_]\w* = )', l)) and l.strip() != ''

def parse_paper(body):
    """Split a question body into prose, student templates (end in YOUR CODE) and given code."""
    text, templates, given, provided = [], [], [], []
    i, n = 0, len(body)
    label_given = False
    while i < n:
        l = body[i]
        if re.match(r'^(def |class |@dataclass)', l):
            block = [l]; i += 1
            in_doc = False
            while i < n:
                cur = body[i]
                in_doc = (sum(b.count('"""') for b in block) % 2 == 1)
                if in_doc and cur and cur[:1] not in ' \t':
                    block[-1] = block[-1] + cur  # PDF wrapped a long docstring line
                elif (cur == '' or cur[:1] in ' \t' or block[-1].startswith('@')) and not cur.startswith('Given ('):
                    block.append(cur)
                else:
                    break
                i += 1
            code = '\n'.join(block).rstrip()
            if i < n and body[i] == 'YOUR CODE':
                templates.append(code); i += 1
            else:
                given.append(code)
            label_given = False
            continue
        if l.startswith('Given (already written'):
            label_given = True
        elif l.startswith('Provided:'):
            provided.append(l[len('Provided:'):].strip())
            i += 1
            while i < n and body[i] and not re.match(r'^(def |class |@dataclass|Given \()', body[i]):
                provided.append(body[i]); i += 1
            continue
        elif l != 'YOUR CODE':
            text.append(l)
        i += 1
    return text, templates, given, provided

def parse_sol(body):
    code, prose, uses = [], [], []
    i = 0
    if body and body[0].startswith('Uses code provided'):
        while i < len(body) and not re.match(r'^(def |class |@)', body[i]):
            uses.append(body[i]); i += 1
    else:
        while i < len(body) and not re.match(r'^(def |class |@|[a-z_]\w* = )', body[i]):
            uses.append(body[i]); i += 1  # wrapped header lines
    for l in body[i:]:
        if not prose and (is_code(l) or l == ''):
            code.append(l)
        else:
            prose.append(l)
    return '\n'.join(code).rstrip(), ' '.join(prose), ' '.join(uses)

exams = []
for paper in sorted(glob.glob(os.path.join(TXT, '*-write-all-code.txt'))):
    base = os.path.basename(paper)[:-4]
    m = re.match(r'61a-(fa|sp|su)(\d\d)-mt2', base)
    term = {'fa': 'Fall', 'sp': 'Spring', 'su': 'Summer'}[m.group(1)] + ' 20' + m.group(2)
    psecs = split_sections(lines_of(paper))
    ssecs = split_sections(lines_of(paper.replace('.txt', '-solutions.txt')))
    assert len(psecs) == len(ssecs), (base, len(psecs), len(ssecs))
    qs = []
    for p, s in zip(psecs, ssecs):
        assert p['qnum'] == s['qnum'], (base, p['qnum'], s['qnum'])
        text, code, given, provided = parse_paper(p['body'])
        scode, prose, uses = parse_sol(s['body'])
        qs.append({'qnum': p['qnum'], 'title': p['title'], 'header': p['header'], 'text': text,
                   'signature': '\n\n'.join(code), 'given': '\n\n'.join(given),
                   'provided': ' '.join(provided), 'solution': scode, 'explanation': prose, 'sol_uses': uses})
    exams.append({'id': base.replace('61a-', '').replace('-mt2-write-all-code', ''), 'term': term, 'questions': qs})
json.dump(exams, open('questions_raw.json', 'w'), indent=1)
print(sum(len(e['questions']) for e in exams), 'questions in', len(exams), 'exams')
