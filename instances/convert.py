#!/usr/bin/env python3
import json

bound = json.loads(input())
print(1)
for coef, index in bound:
    print(f"{coef} {index}")
