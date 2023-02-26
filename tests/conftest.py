from os import walk
from os.path import realpath, dirname, sep, join
import json

def pytest_generate_tests(metafunc):
    if metafunc.function.__name__ != "test_generic":
        return
    test_ids = []
    test_cases = []
    current_dir = join(dirname(realpath(__file__)), 'data')
    for root, dirs, files in walk(current_dir):
        for file in files:
            with open(join(dirname(realpath(__file__)), 'data', file), "r") as f:
                data = json.load(f)
                test_ids.append(file)
                test_cases.append(data)
    metafunc.parametrize("input_expected", test_cases, ids=test_ids)
