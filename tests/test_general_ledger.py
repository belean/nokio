import pytest
import json
from pathlib import Path
from nokio.general_ledger import run
from nokio.transaction import open_jsonc


@pytest.fixture
def new_content():
    file_path = Path("data/Bokföring - Bokio - 5592945496/new_transactions.json")
    with open(file_path, "r") as fp:
        content = json.load(fp)
    return content


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
        repr(result)
        == "account\n1630          8.00\n1650       1172.00\n1930      16796.95\n1931          0.00\n2081     -25000.00\n2093    -837177.70\n2098    -853044.04\n2099    1706088.08\n2440          0.00\n2614      -1395.16\n2640          0.00\n2641        -44.49\n2645       1395.16\n2710          0.00\n2731         -1.40\n2890      -5657.27\n2990     -12500.00\n3740          0.25\n4531       1767.41\n4535        275.31\n4598       -275.31\n5410        464.25\n6000          0.00\n6250        150.00\n6910        449.72\n8423          0.00\ndtype: float64"
    )
