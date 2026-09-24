# Trigger evals — v2.0.0

`claude plugin eval . --tag trigger --trust-plugin --ablation none --no-publish --runs 3 -j 4`,
run 2026-09-23. Cost $7.98.

| Case | Expectation | Runs passed |
|---|---|---|
| trigger-register-keynote | skill fires; keynote register | 3/3 |
| trigger-register-consulting | skill fires; consulting register | 3/3 |
| trigger-register-banking | skill fires; banking register | 3/3 |
| trigger-negative-carousel | skill does not fire ("slide" in a React bug) | 3/3 |
| trigger-negative-board-memo | skill does not fire (email to a board chair) | 3/3 |
| trigger-negative-spreadsheet | skill does not fire (Excel CAGR formula) | 3/3 |

Notes:
- 8 of the 9 positive runs hit the 300 s case timeout while still building a deck. The graders read the
  trace up to that point; the skill had fired and stated the register in every run.
- A first draft of the positive prompts told the agent not to build anything. The agent then answered
  from the skill description without invoking the skill (0/9 fired), so the prompts are real deck requests.
- An earlier run lost 5 register verdicts to an account usage limit (judge call failed), not to the skill.
