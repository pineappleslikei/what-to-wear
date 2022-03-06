import pytest
import main


@pytest.fixture
def client():
    main.app.config['TESTING'] = True

    with main.app.test_client() as client:
        yield client


@pytest.fixture
def zipcode_inputs():
    return {
        'valid': [
            92630,
            33101,
            31001
        ],
        'invalid': [
            '9l789', # letter amongst numbers
            9876, # not enough digits
            'abcde', # letters not numbers
            -19877, # negative int
        ]
    }

def test_validate_zip_code_input(zipcode_inputs):
    valid_results = [main._validate_zip_code_input(zip) for zip in zipcode_inputs['valid']]
    assert False not in valid_results

    invalid_results = [main._validate_zip_code_input(zip) for zip in zipcode_inputs['invalid']]
    assert True not in invalid_results