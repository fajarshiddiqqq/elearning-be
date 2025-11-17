# app/services/submission_service.py
from app.models import Submissions, Feedbacks, TestCases, Rubrics
from app.extensions import db
from .ai_feedback import generate_feedback
import subprocess, tempfile, os


def safe_run_python(code: str, input_data: str) -> str:
    """Execute student code safely with input and capture output"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
        f.write(code.encode())
        temp_path = f.name

    try:
        result = subprocess.run(
            ["python3", temp_path],
            input=input_data.encode(),
            capture_output=True,
            timeout=2
        )
        return result.stdout.decode().strip()
    except subprocess.TimeoutExpired:
        return "__TIMEOUT__"
    except Exception as e:
        return f"__ERROR__: {str(e)}"
    finally:
        os.remove(temp_path)


def run_submission(student_id: int, question_id: int, code: str, generate_ai: bool = True) -> Submissions:
    """Run student's submission, execute test cases, and optionally generate AI feedback."""
    # 1. Get rubric and question
    rubric = Rubrics.query.filter_by(question_id=question_id).first()
    if not rubric:
        raise ValueError("Rubric not found for this question")

    question = rubric.question
    test_cases = question.test_cases
    if not test_cases:
        raise ValueError("No test cases found for this question")

    # 2. Determine attempt number
    last_attempt = Submissions.query.filter_by(student_id=student_id, question_id=question_id)\
                    .order_by(Submissions.attempt_no.desc()).first()
    attempt_no = last_attempt.attempt_no + 1 if last_attempt else 1

    # 3. Create submission
    submission = Submissions(
        question_id=question_id,
        student_id=student_id,
        code=code,
        status="pending",
        attempt_no=attempt_no
    )
    db.session.add(submission)
    db.session.flush()  # Get submission.id

    # 4. Run test cases
    test_results = []
    error_occurred = False

    for tc in test_cases:
        output = safe_run_python(code, tc.input_data)

        if output.startswith("__ERROR__") or output == "__TIMEOUT__":
            submission.status = "error"
            submission.error_message = output
            error_occurred = True
            break

        passed = output == tc.expected_output
        test_results.append({
            "test_case_id": tc.id,
            "input": tc.input_data,
            "expected": tc.expected_output,
            "output": output,
            "passed": passed
        })

    # 5. If no runtime error, set pass/fail
    if not error_occurred:
        submission.status = "passed" if all(r["passed"] for r in test_results) else "failed"

    # 6. Generate AI feedback (optional, can be async later)
    if generate_ai:
        ai_text = generate_feedback(
            code=code,
            rubric_criteria=rubric.criteria,
            tone=rubric.tone,
            test_results=test_results
        )
        feedback = Feedbacks(
            submission_id=submission.id,
            ai_feedback={"text": ai_text},
            teacher_feedback=None,
            final_score=None
        )
        db.session.add(feedback)

    # 7. Commit all
    db.session.commit()

    return submission
