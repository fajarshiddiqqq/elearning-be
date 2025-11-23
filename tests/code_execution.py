# mvp_executor.py
"""
Very simple, UNSAFE MVP code runner for a single Python function.

- Students must implement: sum_two_numbers(a, b)
- We execute their code with exec()
- Then we run test cases against that function
"""

TEST_CASES = [
    # (args, expected_output)
    ((1, 2), 3),
    ((-5, 5), 0),
    ((100, 200), 300),
    ((0, 0), 0),
]


def evaluate_submission(code: str) -> dict:
    """
    Execute user code and run predefined test cases.

    Code must define a function:

        def sum_two_numbers(a, b):
            ...

    Returns a dict with status and per-test details.
    """
    sandbox_globals = {}

    # 1. Execute the submitted code
    try:
        exec(code, sandbox_globals)
    except Exception as e:
        return {
            "status": "error",
            "error": f"Error while executing code: {e!r}",
            "results": [],
        }

    # 2. Get the target function
    func = sandbox_globals.get("sum_two_numbers")
    if func is None or not callable(func):
        return {
            "status": "error",
            "error": "Function 'sum_two_numbers(a, b)' is not defined.",
            "results": [],
        }

    # 3. Run test cases
    results = []
    all_passed = True

    for idx, (args, expected) in enumerate(TEST_CASES, start=1):
        try:
            output = func(*args)
        except Exception as e:
            all_passed = False
            results.append(
                {
                    "case": idx,
                    "status": "error",
                    "input": args,
                    "expected": expected,
                    "error": repr(e),
                }
            )
            continue

        passed = output == expected
        if not passed:
            all_passed = False

        results.append(
            {
                "case": idx,
                "status": "passed" if passed else "failed",
                "input": args,
                "expected": expected,
                "got": output,
            }
        )

    return {
        "status": "passed" if all_passed else "failed",
        "results": results,
    }


# Example of a correct student submission
CORRECT_CODE = """
def sum_two_numbers(a, b):
    return a + b
"""

# Example of an incorrect student submission
WRONG_CODE = """
def sum_two_numbers(a, b):
    # wrong on purpose
    return a - b
"""


if __name__ == "__main__":
    from pprint import pprint

    print("=== Running CORRECT_CODE ===")
    result_correct = evaluate_submission(CORRECT_CODE)
    pprint(result_correct)
    print()

    print("=== Running WRONG_CODE ===")
    result_wrong = evaluate_submission(WRONG_CODE)
    pprint(result_wrong)
    print()

    # You can manually try another snippet here if you want:
    # custom_code = '''
    # def sum_two_numbers(a, b):
    #     return a + b + 1
    # '''
    # print("=== Running custom_code ===")
    # pprint(evaluate_submission(custom_code))
