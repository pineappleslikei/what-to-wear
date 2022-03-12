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

@pytest.fixture
def list_of_raw_temperatures():
    return [35.9, 44.7657657, 80.3, 80.9, 120.8765]


@pytest.fixture
def list_of_clean_temps():
    return [30, 40, 50, 60, 70, 80, 90]

def test_validate_zip_code_input(zipcode_inputs):
    valid_results = [main._validate_zip_code_input(zip) for zip in zipcode_inputs['valid']]
    assert False not in valid_results

    invalid_results = [main._validate_zip_code_input(zip) for zip in zipcode_inputs['invalid']]
    assert True not in invalid_results


def test_clean_temperature_input(list_of_raw_temperatures):
    results = [main._clean_temperature_input(temp) for temp in list_of_raw_temperatures]
    assert results == [36, 45, 80, 81, 121]


def test_get_temp_category(list_of_clean_temps):
    results = [main._get_temp_category(clean_temp) for clean_temp in list_of_clean_temps]
    assert results == [
        main.Category.C1,
        main.Category.C2,
        main.Category.C3,
        main.Category.C4,
        main.Category.C5,
        main.Category.C6,
        main.Category.C7,
    ]