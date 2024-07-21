import pytest
import json
from pathlib import Path
from nokio.general_ledger import run
from nokio.transaction import open_jsonc


@pytest.fixture
def new_content():
    file_path = Path("data/Bokföring - Bokio - 5592945496/new_transactions.json")
    return open_jsonc(file_path)


@pytest.fixture
def content():
    file_path = Path("data/Bokföring - Bokio - 5592945496/out/5592945496_2023.json")
    # with open(file_path, "r") as fp:
    #    content = json.load(fp)
    return open_jsonc(file_path)


@pytest.fixture
def content_jsonc():
    file_path = Path(
        "/Users/backis/Desktop/Bokslut 2023/deklaration_2023/bokföring_sciple_2023.jsonc"
    )
    return open_jsonc(file_path)


def test_run(content, new_content, content_jsonc):
    result = run(content, new_content, content_jsonc)
    assert (
        repr(result.round(2))
        == "account\n1630       165.00\n1650         0.00\n1930     18354.92\n1931         0.00\n2081    -25000.00\n2091    853044.04\n2093   -837177.70\n2098        -0.00\n2099      2287.34\n2440        -0.00\n2614     -2328.44\n2640        -0.00\n2641        44.31\n2645      2328.44\n2710        -0.00\n2731        -1.40\n2890    -11716.51\n2990        -0.00\n3740        -0.00\n4531        -0.00\n4535         0.00\n4598         0.00\n5410         0.00\n6000         0.00\n6250         0.00\n6910         0.00\n8310         0.00\n8423         0.00\n8999         0.00\ndtype: float64"
    )
