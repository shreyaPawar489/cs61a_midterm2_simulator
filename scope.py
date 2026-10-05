"""Topics for the Fall 2026 Midterm 2, following the course's Ed post.

The Ed post says Midterm 2 adds recursion (1.7), sequences (2.2) and linked lists (2.3) to the
Midterm 1 topics, and lists recommended past problems (SCOPE). Every other compiled past-paper
question is tagged with one of the same topics (OTHER_TOPICS) so mock exams draw from all of them.

A problem the Ed post lists with several parts, such as Q5(b)-(c), is one exam question in which
you write every part.
"""

MT1 = 'Midterm 1 topics'
TOPICS = ['Recursion', 'Lists and Dictionaries', 'Linked Lists', MT1]
MAIN_TOPICS = TOPICS[:3]  # every mock exam has one question from each of these

SCOPE = [
    # (topic, Ed title, what it practices, part ids)
    ('Recursion', 'Almost a Perfect Question', 'Tree recursion over divisors', ['fa24-q4-a']),
    ('Recursion', 'Just Add and Multiply', 'Counting and searching + and * expressions', ['sp25-q5-b', 'sp25-q5-c']),
    ('Recursion', 'A Perfect Question', 'Sums of perfect squares', ['fa23-q4-a']),
    ('Recursion', 'Parking', 'Counting parking arrangements', ['sp23-q5-a']),
    ('Recursion', 'Aim for 100', 'Counting subsets that sum to 100', ['fa22-q5-a']),
    ('Recursion', 'Best of Both', 'Switching between two lists', ['fa19-q6']),
    ('Recursion', 'Nonplussed', 'Inserting + signs between digits', ['fa18-q4-a', 'fa18-q4-b']),
    ('Recursion', 'Both Ways', 'Counting paths through function applications', ['fa17-q4-c']),
    ('Recursion', 'Summer Camp (challenge)', 'Recursive lambdas that build lists', ['fa16-q7-b']),
    ('Recursion', 'This One Goes to Eleven', 'Building lists with no adjacent 1s', ['fa14-q3-b']),

    ('Lists and Dictionaries', 'Exclusive', 'Filtering with a list comprehension', ['fa25-q4-a']),
    ('Lists and Dictionaries', 'Two Topping Pizzas', 'Dictionary lookups and string loops', ['fa25-q6-a', 'fa25-q6-b']),
    ("Lists and Dictionaries", "Who's counting?", 'Consecutive integers in lists', ['sp24-q4-a', 'sp24-q4-b']),
    ('Lists and Dictionaries', 'Prefixes', 'Prefix sums with slicing', ['sp23-q3-a']),
    ('Lists and Dictionaries', 'Doctor Change', 'All subset sums of a list', ['fa21-q2-b']),
    ('Lists and Dictionaries', 'Thanos', 'Max and min with key', ['fa21-q4-b', 'fa21-q4-c']),
    ('Lists and Dictionaries', 'Seek Once', 'Comparing nearby elements', ['fa19-q4']),
    ('Lists and Dictionaries', 'Lowest', 'One-line comprehension with min', ['fa18-q2']),
    ('Lists and Dictionaries', 'Pumpkin Splice Latte', 'Splicing lists with slices', ['fa17-q3-a', 'fa17-q3-b']),
    ('Lists and Dictionaries', 'Return of the Digits (challenge)', 'Sets as nested functions', ['fa15-q3-e']),

    ('Linked Lists', 'Exclusive', 'Removing a value', ['fa25-q4-b']),
    ('Linked Lists', 'Just Add and Multiply', 'Alternating * and +', ['sp25-q5-a']),
    ('Linked Lists', 'How Long is this Exam?', 'Longest sublist under a sum limit', ['fa24-q5-a', 'fa24-q5-b']),
    ('Linked Lists', 'After Party', 'Finding one value after another', ['fa23-q6-a-b']),
    ('Linked Lists', 'Prefixes', 'Prefix sums that are multiples of 10', ['sp23-q3-b']),
    ('Linked Lists', 'Yield, Fibonacci!', 'Filtering by index', ['fa20-q2-b']),
    ('Linked Lists', 'Pumpkin Splice Latte', 'Splicing linked lists', ['fa17-q3-c']),
    ('Linked Lists', 'Both Ways', 'Common values in sorted lists', ['fa17-q4-a']),
    ('Linked Lists', 'This One Goes to Eleven', 'Counting adjacent pairs', ['fa14-q3-a']),
]

R, LD, LL = 'Recursion', 'Lists and Dictionaries', 'Linked Lists'
OTHER_TOPICS = {
    'fa14-q5-a': LD, 'fa15-q3-c': LL, 'fa16-q7-a': R, 'fa18-q5-a': LD, 'fa18-q6': LL, 'fa19-q5-a': R,
    'fa20-q3-a': LD, 'fa20-q3-b': LD, 'fa20-q3-c': LD, 'fa21-q2-a': R, 'fa21-q4-a': LD, 'fa22-q3-b': LD, 'fa22-q6-a': LD,
    'fa23-q4-b': R, 'fa23-q4-b-iv': LD, 'fa24-q4-b': R, 'fa24-q4-c': LD, 'fa24-q4-c-blank-l': LD,
    'fa25-q6-c': R, 'fa25-q6-d': R, 'sp15-q3-d': LL, 'sp15-q4-b': R, 'sp16-q3-a': LL,
    'sp18-q3-a': LD, 'sp18-q3-b': LD, 'sp18-q3-c': LD, 'sp18-q4-a': LL, 'sp18-q4-b': R, 'sp19-q3': R,
    'sp20-q2-a': R, 'sp20-q2-b': R, 'sp20-q3-a': LL, 'sp21-q4': LL, 'sp21-q6-b-c': LD, 'sp21-q7': MT1,
    'sp22-q1-c': R, 'sp22-q3': MT1, 'sp22-q4': LL, 'sp22-q8-c': LD, 'sp22-q8-d': LD,
    'sp23-q5-b': R, 'sp23-q5-c': R, 'sp24-q4-c': R, 'sp25-q5-d': R, 'sp26-q7': R, 'sp26-q8': LL,
    'su20-q2': R, 'su20-q3-microscope': MT1, 'su20-q3-plush': MT1, 'su20-q5': MT1, 'su20-q6': LD,
    'su21-q2-a': MT1, 'su21-q2-b': R, 'su21-q4': R, 'su21-q5-b': MT1,
    'su22-q3-a': MT1, 'su22-q3-b': MT1, 'su22-q4': R, 'su22-q5': MT1, 'su22-q6-a': R, 'su22-q6-b': R,
    'su22-q8-b': LD, 'su23-q3-a': MT1, 'su23-q3-b': MT1, 'su23-q3-c': MT1, 'su23-q4': MT1,
    'su23-q5-a': R, 'su23-q5-b': R, 'su23-q5-c': R, 'su24-q4-a': LD, 'su24-q4-b': R, 'su24-q6': R,
    'su25-q3-a': LD, 'su25-q3-b': LD, 'su25-q4-a': R, 'su25-q4-b': R,
}
