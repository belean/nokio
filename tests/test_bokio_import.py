import pytest
from pathlib import Path
import json
from nokio.bokio_import import (
    transform_bokio_import,
    # current_saldo,
    convert_trans,
    convert_META,
    convert_KONTO,
    convert_IB,
    convert_RES,
    convert_UB,
    # any_saldo,
)
from nokio import open_jsonc
from tests.data.expected_results import bokio_import_expected_result


@pytest.fixture
def import_file():
    return Path("tests/data/bokio_test_import_2023.se")


@pytest.fixture
def out_file():
    return Path("tests/data/out/bokio_test_import_2023.jsonc")


def test_transform_bokio_import(import_file, out_file):
    result = transform_bokio_import(import_file)
    # transform_bokio_import creates the out_file
    content = open_jsonc(out_file)
    assert repr(content) == bokio_import_expected_result


@pytest.fixture
def tot():
    return dict(IB={}, UB={}, RES={}, KONTO={}, META={"RAR": {}}, TRANS={})


def test_convert_trans(tot):
    transes = [
        ' "V" "1" 20230114 "Förbrukningsinventarier" 20230121\n{\n\t#TRANS 2640 {} 154.75\n\t#TRANS 2890 {} -619.00\n\t#TRANS 5410 {} 464.25\n}\n',
        ' "V" "2" 20230101 "Periodisering" 20230121\n{\n\t#TRANS 2990 {} 6250.00\n\t#TRANS 6000 {} -6250.00\n}\n',
        ' "V" "3" 20230116 "Förseningsavgift" 20230121\n{\n\t#TRANS 1630 {} 6250.00\n\t#TRANS 1630 {} -6250.00\n\t#TRANS 1930 {} -6250.00\n\t#TRANS 2990 {} 6250.00\n\t#TRANS 6000 {} -6250.00\n\t#TRANS 8423 {} 6250.00\n}\n',
        ' "V" "4" 20230102 "Omprövning moms jul-sep2022" 20230121\n{\n\t#TRANS 1630 {} 10.00\n\t#TRANS 1650 {} -10.00\n}\n',
        ' "V" "5" 20230116 "Annullering av V3: Förseningsavgift" 20230121\n{\n\t#TRANS 1630 {} -6250.00\n\t#TRANS 1630 {} 6250.00\n\t#TRANS 1930 {} 6250.00\n\t#TRANS 2990 {} -6250.00\n\t#TRANS 6000 {} 6250.00\n\t#TRANS 8423 {} -6250.00\n}\n',
    ]
    for trans in transes:
        result = convert_trans(trans)
        tot["TRANS"][result.verificate] = result.model_dump(exclude="verificate")
    assert (
        repr(tot["TRANS"])
        == "{1: {'date': datetime.date(2023, 1, 14), 'name': 'Förbrukningsinventarier', 'description': None, 'recorded_at': datetime.datetime(2023, 1, 21, 0, 0), 'account': {'2640D': 154.75, '2890K': 619.0, '5410D': 464.25}, 'frozen': None}, 2: {'date': datetime.date(2023, 1, 1), 'name': 'Periodisering', 'description': None, 'recorded_at': datetime.datetime(2023, 1, 21, 0, 0), 'account': {'2990D': 6250.0, '6000K': 6250.0}, 'frozen': None}, 3: {'date': datetime.date(2023, 1, 16), 'name': 'Förseningsavgift', 'description': None, 'recorded_at': datetime.datetime(2023, 1, 21, 0, 0), 'account': {'1630D': 6250.0, '1630K': 6250.0, '1930K': 6250.0, '2990D': 6250.0, '6000K': 6250.0, '8423D': 6250.0}, 'frozen': None}, 4: {'date': datetime.date(2023, 1, 2), 'name': 'Omprövning moms jul-sep2022', 'description': None, 'recorded_at': datetime.datetime(2023, 1, 21, 0, 0), 'account': {'1630D': 10.0, '1650K': 10.0}, 'frozen': None}, 5: {'date': datetime.date(2023, 1, 16), 'name': 'Annullering av V3: Förseningsavgift', 'description': None, 'recorded_at': datetime.datetime(2023, 1, 21, 0, 0), 'account': {'1630K': 6250.0, '1630D': 6250.0, '1930D': 6250.0, '2990K': 6250.0, '6000D': 6250.0, '8423K': 6250.0}, 'frozen': None}}"
    )


def test_convert_META(tot):
    # tot: dict = dict(IB={}, UB={}, RES={}, KONTO={}, META={"RAR": {}}, TRANS={})
    rows = ["#FORMAT PC8", "#ORGNR 5599998989", '#FNAMN "Nokio Test AB"']
    for row in rows:
        convert_META(tot, row)
    assert (
        repr(tot)
        == "{'IB': {}, 'UB': {}, 'RES': {}, 'KONTO': {}, 'META': {'RAR': {}, 'FORMAT': 'PC8', 'ORGNR': '5599998989', 'FNAMN': 'Nokio Test AB'}, 'TRANS': {}}"
    )


def test_convert_KONTO(tot):
    rows = [
        '#KONTO 1010 "Utvecklingsutgifter"',
        "#SRU 1010 7201",
        '#KONTO 1930 "Företagskonto / affärskonto"',
        "#SRU 1930 7281",
    ]
    for row in rows:
        convert_KONTO(tot, row)
    assert (
        repr(tot["KONTO"])
        == "{'1010': {'Namn': 'Utvecklingsutgifter', 'SRU': '7201'}, '1930': {'Namn': 'Företagskonto / affärskonto', 'SRU': '7281'}}"
    )


def test_convert_IB(tot):
    rows = ["#IB -1 1630 10262.00", "#IB 0 1630 -2.00"]
    for row in rows:
        convert_IB(tot, row)
    assert repr(tot["IB"]) == "{'1630': {'-1': '10262.00', '0': '-2.00'}}"


def test_convert_RES(tot):
    rows = ["#RES -1 3308 -23.48", "#RES -1 3740 -1.62"]
    for row in rows:
        convert_RES(tot, row)
    assert repr(tot["RES"]) == "{'3308': {'-1': '-23.48'}, '3740': {'-1': '-1.62'}}"


def test_convert_UB(tot):
    rows = ["#UB -2 1630 10262.00", "#UB -1 1630 -2.00"]
    for row in rows:
        convert_UB(tot, row)
    assert repr(tot["UB"]) == "{'1630': {'-2': '10262.00', '-1': '-2.00'}}"


@pytest.fixture
def content():
    file_path = Path("tests/data/out/bokio_test_import_2023.jsonc")
    # with open(file_path, "r") as fp:
    #    content = json.load(fp)
    return open_jsonc(file_path)


# def test_any_saldo(content):
#    result = any_saldo(content, 1630, 0)
#    assert repr(result) == "np.float64(-2.0)"
#    result = any_saldo(content, 1630, 100)
#    assert repr(result) == "np.float64(8.0)"
#    result = any_saldo(content, 1930, 6)
#    assert repr(result) == "np.float64(16796.95)"
#    result = any_saldo(content, 1930)
#    assert repr(result) == "np.float64(16796.95)"
