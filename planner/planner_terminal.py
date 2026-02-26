from fastapi import HTTPException

from planner.models import PlannerHistory
from planner.planner_service import PlannerService


def _display_state(history: PlannerHistory | None, n_scenes: int) -> None:
    """Print current chat history and most recent plan to the terminal."""
    print("\n" + "=" * 60)
    print(f"  n_scenes = {n_scenes}")
    print("=" * 60)
    if history is None:
        print("  (no history yet)")
        print("  Enter a prompt to create an initial plan.")
    else:
        print("  CHAT HISTORY")
        print("-" * 40)
        for i, item in enumerate(history.items, 1):
            user_content = getattr(item.user, "content", str(item.user))
            ai_content = getattr(item.ai, "content", str(item.ai))
            print(f"  [{i}] User: {user_content[:80]}{'...' if len(str(user_content)) > 80 else ''}")
            print(f"      AI:  {ai_content[:80]}{'...' if len(str(ai_content)) > 80 else ''}")
        print("-" * 40)
        print("  CURRENT PLAN (scene prompts)")
        print("-" * 40)
        for j, p in enumerate(history.plan.prompts, 1):
            print(f"  {j}. {p[:70]}{'...' if len(p) > 70 else ''}")
    print("=" * 60)
    print("  Commands: /revert N  /revert_edit N <prompt>  /n_scenes N  /quit")
    print("  Or type a message to plan or edit.")
    print()


def run_planning_repl(n_scenes: int = 5) -> PlannerHistory | None:
    """
    Run an interactive terminal session: show chat history and latest plan,
    and accept either chat input (to call plan/plan_revert_edit) or commands.
    Returns the final history when the user quits, or None if no plan was created.
    """
    history: PlannerHistory | None = None
    while True:
        _display_state(history, n_scenes)
        try:
            line = input("> ").strip()
        except EOFError:
            print()
            break
        if not line:
            continue
        if line.startswith("/quit") or line.startswith("/exit"):
            break
        if line.startswith("/n_scenes "):
            try:
                n_scenes = int(line.split(maxsplit=1)[1])
                print(f"  n_scenes set to {n_scenes}")
            except (IndexError, ValueError):
                print("  Usage: /n_scenes <integer>")
            continue
        if line.startswith("/revert "):
            rest = line.split(maxsplit=1)[1] if len(line.split(maxsplit=1)) > 1 else ""
            try:
                n = int(rest.strip())
            except ValueError:
                print("  Usage: /revert <integer>")
                continue
            if history is None:
                print("  No history to revert.")
                continue
            try:
                history = PlannerService(history).revert(n)
                print(f"  Reverted to last {n} steps.")
            except HTTPException as e:
                print(f"  Error: {e}")
            continue
        if line.startswith("/revert_edit "):
            parts = line.split(maxsplit=2)
            if len(parts) < 3:
                print("  Usage: /revert_edit <N> <prompt>")
                continue
            try:
                n = int(parts[1])
                prompt = parts[2]
            except ValueError:
                print("  Usage: /revert_edit <integer> <prompt>")
                continue
            if history is None:
                print("  No history to revert.")
                continue
            try:
                history = PlannerService(history).revert_edit(prompt, n_scenes)
                print("  Reverted and applied edit.")
            except HTTPException as e:
                print(f"  Error: {e}")
            continue
        # Plain chat input: call plan()
        try:
            history = PlannerService(history).plan(line, n_scenes)
        except Exception as e:
            print(f"  Error: {e}")
    return history



