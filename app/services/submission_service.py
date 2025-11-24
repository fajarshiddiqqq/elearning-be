import time

def evaluate_python_code(code: str, test_cases: list, function_name: str):
    sandbox_globals = {}

    try:
        exec(code, sandbox_globals)
    except Exception as e:
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "results": [],
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "execution_time_ms": 0
        }

    func = sandbox_globals.get(function_name)
    if not callable(func):
        return {
            "status": "error",
            "error_type": "FunctionNotFound",
            "error_message": f"Function '{function_name}' not found.",
            "results": [],
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "execution_time_ms": 0
        }

    results = []
    passed_count = 0
    failed_count = 0

    start = time.time()

    for idx, (args, expected) in enumerate(test_cases, start=1):
        # normalize args: always a tuple
        if isinstance(args, (list, tuple)):
            call_args = tuple(args)
        else:
            call_args = (args,)

        try:
            output = func(*call_args)
        except Exception as e:
            failed_count += 1
            results.append({
                "case": idx,
                "status": "error",
                "input": list(call_args),
                "expected": expected,
                "error_type": type(e).__name__,
                "error_message": str(e)
            })
            continue

        if output == expected:
            passed_count += 1
            results.append({
                "case": idx,
                "status": "passed",
                "input": list(call_args),
                "expected": expected,
                "got": output
            })
        else:
            failed_count += 1
            results.append({
                "case": idx,
                "status": "failed",
                "input": list(call_args),
                "expected": expected,
                "got": output
            })

    end = time.time()

    return {
        "status": "passed" if failed_count == 0 else "failed",
        "total_tests": len(test_cases),
        "passed": passed_count,
        "failed": failed_count,
        "execution_time_ms": round((end - start) * 1000, 3),
        "results": results
    }
