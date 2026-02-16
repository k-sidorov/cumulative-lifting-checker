#!/usr/bin/env python3
import re
import ast

import itertools
import json
from math import ceil
from pathlib import Path
import sys


def _parse_value(val):
    val = val.strip()

    # 2D array: [| row | row |]
    if val.startswith("[|"):
        inner = val[2:-1].strip()   # remove [| and ]
        rows = []

        for row in inner.split("|"):
            row = row.strip()
            if not row:
                continue
            rows.append(ast.literal_eval("[" + row + "]"))

        return rows

    # 1D array or set
    if val.startswith("["):
        return ast.literal_eval(val)

    # scalar
    return ast.literal_eval(val)


def parse_dzn(filename):
    data = {}

    with open(filename, "r") as f:
        text = f.read()

    # Remove comments
    text = re.sub(r"%.*", "", text)

    # Split entries
    entries = [e.strip() for e in text.split(";") if e.strip()]

    for entry in entries:
        name, val = entry.split("=", 1)
        name = name.strip()
        val = val.strip()

        data[name] = _parse_value(val)

    return data


def main(data_file, cons_file):
    data = parse_dzn(data_file)
    if 'rr' not in data or 'rcap' not in data or 'dur' not in data:
        print('Cannot find key `rr` in the data file')
        sys.exit(1)
    arr = data['rr']
    cap = data['rcap']
    dur = data['dur']
    n_cons, n_tasks = len(arr), len(arr[0])
    rhs, terms = None, [0 for _ in range(n_tasks)]
    for line in cons_file.open():
        tokens = [int(x) for x in line.split()]
        if len(tokens) == 1:
            rhs, = tokens
        elif len(tokens) == 2:
            coef, index = tokens
            terms[index] = coef
    # Verification: go over all combinations of size (rhs + 1) that violate
    # the verified inequality, check if all of them violate at least one
    # of the input inequality
    nonzeros = [ix for ix in range(n_tasks) if terms[ix] > 0]
    for support in itertools.combinations(nonzeros, rhs + 1):
        if sum(terms[ix] for ix in support) <= rhs:
            continue
        if all(sum(arr[cons][ix] for ix in support) <= cap[cons] for cons in range(n_cons)):
            print(f'Found an offending set {support}')
            sys.exit(1)
    # Compute the capacity lower bound (weighted sum of used task durations
    # divided by capacity, rounded up)
    print('Checked!')
    bound = int(ceil(float(sum(d * w for d, w in zip(dur, terms))) / rhs))
    print(f'Bound value: {bound}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: check-cumulative.py <data file> <constraint_file>')
        sys.exit(1)
    _, data_file, cons_file = sys.argv
    main(Path(data_file), Path(cons_file))

