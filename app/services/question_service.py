def validate_test_cases(test_cases):
    for tc in test_cases:
        if 'input_data' not in tc or 'expected_output' not in tc:
            raise ValueError("Each test case must have 'input_data' and 'expected_output'")
        if not isinstance(tc.get('is_hidden', False), bool):
            raise ValueError("'is_hidden' must be a boolean")

def validate_rubric(rubric):
    if 'criteria' not in rubric or not isinstance(rubric['criteria'], list):
        raise ValueError("Rubric must have a list of criteria")
    total_weight = 0
    for c in rubric['criteria']:
        if 'aspect' not in c or 'weight' not in c or 'description' not in c:
            raise ValueError("Each rubric criterion must have 'aspect', 'weight', and 'description'")
        total_weight += c['weight']
    if not abs(total_weight - 1.0) < 1e-6:
        raise ValueError("Rubric weights must sum to 1")