from src.utils import sanitize_filename

def test_sanitize_filename_standard():
    assert sanitize_filename("NormalFilename") == "NormalFilename"

def test_sanitize_filename_with_spaces():
    assert sanitize_filename("Filename with spaces") == "Filename with spaces"

def test_sanitize_filename_illegal_chars():
    # Windows/Unixで禁止されがちな文字
    # \ / * ? : " < > |
    input_name = 'Chapter: 1/2 "Introduction"'
    expected = 'Chapter_ 1_2 _Introduction_'
    assert sanitize_filename(input_name) == expected

def test_sanitize_filename_mixed():
    assert sanitize_filename("Part 1: The Beginning?") == "Part 1_ The Beginning_"
