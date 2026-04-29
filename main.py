"""Point d'entrée : lance la question demandée en argument.

    uv run python main.py q2
    uv run python main.py q3
    uv run python main.py q4
"""

import sys


def main():
    if len(sys.argv) < 2:
        print("usage: python main.py {q2,q3,q4}")
        sys.exit(1)
    target = sys.argv[1]
    if target == "q2":
        from src.q2_basic_analysis import main as run
    elif target == "q3":
        from src.q3_assortativity import main as run
    elif target == "q4":
        from src.q4_link_prediction.run import main as run
    else:
        print(f"inconnu : {target}")
        sys.exit(1)
    run()


if __name__ == "__main__":
    main()
