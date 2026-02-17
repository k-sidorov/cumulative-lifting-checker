# Verification for implied lifted `cumulative`s

This repository provides the data and verification scripts for the "search-less" lower bounds reported in Table 4 of the paper “On inferring cumulative constraints.”

## Verification logic

A newly inferred constraint $\sum_{i \in T} w_i \langle x_i \mid d_i \rangle \le r$ is valid if every subset $S \subseteq T$ of tasks that violates the new constraint (i.e., $\sum_{i \in S} w_i > r$) is impossible to execute in parallel according to one of the resource constraints stated in the problem instance. More formally, if the instance contains $m$ constraints $\sum_{j \in T} a_{ij}\langle x_i \mid d_i \rangle \le b_i$ for $i$ from 1 to $m$, then the following implication should hold:

$$ \forall S \subseteq T : \sum_{i \in S} w_i > r \implies \left(\exists j : \sum_{i \in S} a_{ji} > b_j \right). $$

The checker script implements this logic by:
- considering the support of the verified constraint, that is, the set of indices $i$ such that $w_i \neq 0$,
- iterates over all subsets of support of size $(r+1)$, and
- verifies that each subset is falsified by at least one of the original resource capacities.

Iterating over sets of size $(r+1)$ is sufficient, because any smaller offending subset can be trivially extended to the required size. On the other hand, if there is a larger offending subset $S' \subseteq T$ with $S' > r + 1$, then it has to have a redundant element, because all coefficients in the constraints are integers.

## Repository structure

* `check-cumulative.py`: the verification executable.
* `instances/<collection_name>`: contains `.dzn` files for the relevant benchmark instances and `.cons` files that contain the constraint supporting the lower bound in Table 4.

## Getting started

The verification code runs on Python 3.6 or newer, with no external dependencies required. To verify the lower bound for a specific instance (for example, #2 from UBO1000), run:

```bash
python3 check-cumulative.py instances/testset_ubo1000_converted/PSP2.dzn instances/testset_ubo1000_converted/PSP2.cons
```

There are two possible outputs (aside from the parsing/IO errors). When the script **verifies** the validity of the constraint, it outputs two lines:

```
Checked!
Bound value: <bound value>
``` 

The latter line contains the capacity bound, which for the files in the repository should match the values reported in the paper.

When the script manages to **invalidate** a constraint, it outputs a single line:

```
Found an offending set <indices>
```

⚠️ This should not happen on the files distributed in this repository. ⚠️

## Note on computational complexity

The verification code examines $\binom{n}{r+1}$ combinations, which for most distributed instances is negligible (since they have $r = 1$). However, this takes much longer for constraints with non-unit capacities; this is the case, for example, for the constraint for instance #6 from UBO1000, where this code has to verify $\binom{438}{4}$, or approximately 1.5 billion task combinations, and runs for around 30 minutes on a modern desktop.
