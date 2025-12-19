#!/usr/bin/env python3

"""Test different regex patterns"""

import re

pattern = r"etc:\s*-?\d+(?:\.\d+)?(?!$)"

tests = [
    "etc: 3.14",
    "prefix etc: 3.14",
    "etc: 3.14 suffix",
    "prefix etc: 3.14",
    "etc: 3.14",
    "prefix etc: 42 end",
    "prefix etc: -0.5 end",
    "prefix etc: end",
    "prefix etc: ,",
]

for t in tests:
    print(bool(re.compile(pattern).search(t)), t)
