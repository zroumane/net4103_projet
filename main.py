"""Point d'entrée : uv run python main.py {q2,q3,q4,q4e,q5,q6}"""

import sys


def main():
    if len(sys.argv) < 2:
        print("usage: python main.py {q2,q3,q4,q4e,q5,q6}")
        sys.exit(1)
    target = sys.argv[1]
    if target == "q2":
        from src.q2_basic_analysis import main as run
    elif target == "q3":
        from src.q3_assortativity import main as run
    elif target == "q4":
        from src.q4_link_prediction.run import main as run
    elif target == "q4e":
        from src.q4_link_prediction.run_gnn import main as run
    elif target == "q5":
        from src.q5_label_propagation.run import main as run
    elif target == "q6":
        from src.q6_communities.run import main as run
    else:
        print(f"inconnu : {target}")
        sys.exit(1)
    run()


if __name__ == "__main__":
    main()
