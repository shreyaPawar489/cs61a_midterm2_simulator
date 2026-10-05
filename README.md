# CS 61A Midterm 2 simulator

A local, PrairieLearn-style practice environment for the CS 61A Midterm 2 (Fall 2026 scope: recursion,
sequences, linked lists, plus Midterm 1 topics). You write code for past-exam questions in the browser, and each
check runs your Python against visible doctests and hidden tests, the way the CBTF exam does.

## Run it

You need Python 3.9 or newer. There's nothing else to install.

```bash
git clone https://github.com/shreyaPawar489/cs61a_midterm2_simulator.git
cd cs61a_midterm2_simulator
python3 server.py        # opens http://localhost:6161
```

On a Mac you can also double-click `start.command`. Stop the server with Ctrl+C.

## What's in it

- **105 questions** from CS 61A Midterm 2 papers, Fall 2014 to Spring 2026. Each is rewritten as "write all the
  code" (function header, docstring and doctests only) and updated to current notation (`()` is the empty linked
  list, and a `Link` prints as `(3 4 5)`).
- **Topics** come from the course's list of in-scope problems: Recursion, Lists and Dictionaries, Linked Lists, and
  Midterm 1 topics. The 29 problems the course recommends are starred. The tags are in `scope.py`.
- **Mock exam (CBTF format)**: one Recursion, one Lists and Dictionaries and one Linked Lists question, plus a fourth
  from any topic, each from a different past paper. They're worth 5/6/7/8 points (26 total). The score is capped at
  20, and you earn 5 A+ points if all four are fully correct.
- **Exam rules**: there's a timer you can pause and resume, 100 checks per question, and a 5-second grading limit.
  `print("DEBUG: ...")` output is shown and doesn't affect grading. Solutions unlock when the exam closes.
- **Past-paper mode** gives you one whole paper. The **question bank** is untimed, with a "Show solution" button.
- **Grading**: each check runs the visible doctests plus hidden edge-case tests. The hidden tests' expected outputs
  come from the reference solutions, and partial credit is the fraction of tests passed.
- **Study guides**: put PDFs in `study-guides/` and they're linked on every exam page.

Your progress is saved in `state.json`, which stays local and is never committed. Delete it to start fresh.

## Files

| File | Purpose |
|---|---|
| `server.py` | Local web server (Python standard library only) |
| `index.html` | The whole UI |
| `grader.py` | Runs a submission in a separate process with a time limit |
| `prelude.py` | The `Link` class available to every question |
| `exam_data.json` | Questions, reference solutions, doctests and hidden tests |
| `scope.py` | Topic tags and the recommended problem list |
| `hidden_tests.py` | Hidden test inputs (expected outputs are generated) |
| `build_*.py`, `validate.py` | One-time build steps that produced `exam_data.json` |

After editing `scope.py` or `hidden_tests.py`, run `python3 build_final.py` and restart the server.

Questions are adapted from past CS 61A exams published at cs61a.org, for personal study.
