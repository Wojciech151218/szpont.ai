from dotenv import load_dotenv

load_dotenv()

from planner_terminal import run_planning_repl

if __name__ == "__main__":
    run_planning_repl(n_scenes=5)