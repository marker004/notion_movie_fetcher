from shared_items.utils import convert_runtime, strip_all_punctuation


def test_convert_runtime_converts_minutes_to_proper_format_normal():
    runtime = 152
    output = convert_runtime(runtime)
    expected_output = "2:32"

    assert output == expected_output


def test_convert_runtime_converts_minutes_to_proper_format_zero():
    runtime = 0
    output = convert_runtime(runtime)
    expected_output = "0:00"

    assert output == expected_output


def test_strip_all_punctuation():
    test_string = "abc123!@#$%^&*()_~\":'?><,.“‘”’"
    output = strip_all_punctuation(test_string)
    expected_output = "abc123"

    assert output == expected_output
