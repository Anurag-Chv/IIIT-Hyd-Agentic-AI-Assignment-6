from Common.llm import chat


PLANNER_SYSTEM = """
You are the planning component of InboxHero.

Before processing the inbox, produce:
1. One concise Goal.
2. A numbered Plan covering the major steps.

Consider:
- rule-based handling before the model
- retrieving earlier messages when context is needed
- suspicious or hostile instructions
- human approval for irreversible actions
- recording decisions and evidence
- producing the required results

Do not execute actions.
Do not invent information.

Format:

Goal:
<short statement>

Plan:
1. <first step>
2. <second step>
3. <third step>
...
""".strip()


def create_plan(user_question):
    prompt = (
        f"User request:\n{user_question}\n\n"
        "Create the Goal and Plan for this request."
    )
    return chat(prompt, system=PLANNER_SYSTEM)


def display_plan(plan_text):
    print("\n--- Planning Stage ---")
    print(plan_text.strip())
    print("----------------------\n")


if __name__ == "__main__":
    plan = create_plan(
        "Process the inbox and identify what needs my attention."
    )
    display_plan(plan)