"""
This entrypoint is kept for backward compatibility.
Preferred usage: `python eval/evaluation.py run-all --api http://localhost:8000`
or run a single case with `python eval/evaluation.py run sample_basic`.
"""

from eval.evaluation import main  # type: ignore

if __name__ == "__main__":
    print("Note: evaluation has moved to eval/evaluation.py. Redirecting...", file=sys.stderr)
    main()
