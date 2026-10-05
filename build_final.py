"""Attach hidden tests (expected output from the reference solution) and display fields."""
import json
import re
import sys
import grader
from hidden_tests import HIDDEN

exams = json.load(open('questions.json'))
problems = 0
for e in exams:
    for q in e['questions']:
        # Header: "Q5(a)  muladd Spring 2025 MT2 Q5(a) · adapted: ..." plus wrapped continuation lines.
        text = list(q['text'])
        note = q['header'].split('·', 1)[1].strip() if '·' in q['header'] else ''
        while note and text and text[0][:1].islower():
            note += ' ' + text.pop(0)
        q['note'] = note
        paras, cur = [], []
        for line in text + ['']:
            if line.strip():
                cur.append(line.strip())
            elif cur:
                paras.append(' '.join(cur)); cur = []
        q['paragraphs'] = paras
        q['provided_text'] = ' '.join(l.strip() for l in q['provided'].split('\n')) if isinstance(q['provided'], str) else ''

        # Expected hidden outputs come from the reference solution.
        q['hidden'] = [{'source': src, 'want': ''} for src in HIDDEN.get(q['id'], [])]
        rep = grader.grade(q, q['solution'])
        if rep.get('setup_error') or rep.get('timeout') or rep.get('crash'):
            print('REFERENCE BROKE', q['id'], rep.get('setup_error') or rep.get('crash') or 'timeout'); problems += 1; continue
        for h, t in zip(q['hidden'], [t for t in rep['tests'] if t['hidden']]):
            if 'Traceback' in t['got']:
                print('HIDDEN ERRORS ON REFERENCE', q['id'], h['source'], t['got'].splitlines()[-1]); problems += 1
            h['want'] = t['got']
        # Re-grade the reference with the recorded answers: must be 100%.
        rep = grader.grade(q, q['solution'])
        if rep['score'] != 1.0:
            problems += 1
            print('REFERENCE NOT 100%', q['id'], [ (t['name'], t['expected'], t['got']) for t in rep['tests'] if not t['passed']])
        if not q['hidden']:
            print('NO HIDDEN TESTS', q['id'])
        n_vis = sum(1 for t in rep['tests'] if not t['hidden'] and t['name'] != 'doctest setup')
        q['n_visible'] = n_vis

# ---- Ed-post scope: one exam question per listed problem (multi-part problems are merged) ----
from scope import SCOPE, OTHER_TOPICS
BYID = {q['id']: q for e in exams for q in e['questions']}
EXAM_OF = {q['id']: e for e in exams for q in e['questions']}
for q in BYID.values():
    q['topic'], q['ed'] = OTHER_TOPICS.get(q['id']), False
for topic, ed_title, blurb, ids in SCOPE:
    parts = [BYID[i] for i in ids]
    if len(parts) == 1:
        q = parts[0]
    else:
        first = parts[0]
        nums = [p['qnum'] for p in parts]
        letters = [re.search(r'\(([a-z])\)', n).group(1) for n in nums]
        q = {
            'id': '+'.join(ids), 'qnum': nums[0] + '–(' + letters[-1] + ')',
            'title': ' and '.join(p['title'] for p in parts),
            'header': first['header'], 'note': '; '.join(dict.fromkeys(p['note'] for p in parts if p['note'])),
            'paragraphs': [f'({l}) ' + ' '.join(p['paragraphs']) for l, p in zip(letters, parts)],
            # Later parts lean on earlier parts; here you write those too, so drop "from part (a)" notes.
            'provided_text': ' '.join(p['provided_text'] for i, p in enumerate(parts)
                                      if p['provided_text'] and not (i and re.search(r'part \(|previous part', p['provided_text']))),
            'given': '\n\n'.join(dict.fromkeys(p['given'] for p in parts if p['given'])),
            'setup': first['setup'],
            'signature': '\n\n\n'.join(p['signature'] for p in parts),
            'tests_src': '\n'.join(p['tests_src'] for p in parts),
            'hidden': [h for p in parts for h in p['hidden']],
            'solution': '\n\n'.join(p['solution'] for p in parts),
            'explanation': ' '.join(f'({l}) ' + p['explanation'] for l, p in zip(letters, parts)),
            'sol_uses': '', 'provided': '', 'text': [], 'composite': ids,
        }
        rep = grader.grade(q, q['solution'])
        if rep['score'] != 1.0:
            problems += 1
            print('MERGED REFERENCE NOT 100%', q['id'], rep.get('setup_error'), [t['name'] for t in rep['tests'] if not t['passed']])
        q['n_visible'] = sum(1 for t in rep['tests'] if not t['hidden'] and t['name'] != 'doctest setup')
        for p in parts:
            p['part_of'] = q['id']
        EXAM_OF[ids[0]]['questions'].append(q)
    q['topic'], q['ed_title'], q['blurb'], q['ed'] = topic, ed_title, blurb, True
untagged = [q['id'] for e in exams for q in e['questions'] if not q['topic'] and not q.get('part_of')]
if untagged:
    problems += 1
    print('NO TOPIC:', untagged)

json.dump(exams, open('exam_data.json', 'w'), indent=1)
print('problems:', problems, '| questions:', sum(len(e['questions']) for e in exams))
