# Requirements Checklist

Missing more than 2 site requirements = zero credit. After each phase, check
off what is done and name the exact function or field that satisfies it.

## Site

- [ ] At least 7 routes — _where:_
- [ ] At least 5 pages — _where:_
- [ ] `State` dataclass with at least 4 fields — _where:_
- [ ] At least one State field is a list/dict of a second dataclass — _where:_
- [ ] At least 4 State fields, including that list/dict, are meaningfully
      modified in at least one route — _where:_
- [ ] At least 3 input fields (TextBox, CheckBox, SelectBox, TextArea)
      — _where:_
- [ ] At least 3 meaningful if statements — _where:_
- [ ] At least 1 loop over the list/dict of dataclass instances, used in a
      meaningful way — _where:_
- [ ] Legitimate purpose (entertainment: it's a game) — _where:_
- [ ] No global variables; only ALL_CAPS constants, never mutated — _where:_
- [ ] Uses Drafter — _where:_
- [ ] Any technique not covered in the course is explained in a comment or
      docstring — _where:_

## Code quality

- [ ] Good, descriptive variable and function names
- [ ] Every route has at least one `assert_equal` unit test, unless it uses
      randomness (and its docstring says so) — _where:_
- [ ] Lines under 80 characters (hard limit 120)
- [ ] Type hints on every function header
- [ ] A docstring as the first line of every function body
- [ ] Long functions broken into helper functions

## Repository

- [ ] `set_site_information(...)` called in `main.py` — _where:_
- [ ] Planning document in the repo (`docs/`) — _where:_
- [ ] Linked demo video — _where:_
- [ ] All AI conversations in the repo (`ai_conversations/`) — _where:_
