import pytest
from pathlib import Path
import json
from nokio.bokio_import import (
    run,
    generate_general_ledger,
    get_GL_accounts,
    get_GL_sum,
    get_GL_transaction,
    get_IB,
    current_saldo,
)


def test_run():
    run(Path("data/Bokföring - Bokio - 5592945496") / "5592945496_2023.se")


@pytest.fixture
def content():
    file_path = Path("data/Bokföring - Bokio - 5592945496/out/5592945496_2023.json")
    with open(file_path, "r") as fp:
        content = json.load(fp)
    return content


def test_generate_general_ledger(content):
    result = generate_general_ledger(content)
    assert result.shape == (16, 18)


def test_get_GL_accounts(content):
    df_gl = generate_general_ledger(content)
    result = get_GL_accounts(df_gl, "1930")
    assert (
        repr(result)
        == "1        NaN\n2        NaN\n3    -6250.0\n4        NaN\n5     6250.0\n6    -6250.0\n7        NaN\n8        NaN\n9        NaN\n10       NaN\n11       NaN\n12       NaN\n13       NaN\n14       NaN\n15       NaN\n16       NaN\nName: 1930, dtype: float64"
    )


def test_get_GL_sum(content):
    df_gl = generate_general_ledger(content)
    result = get_GL_sum(df_gl)
    assert (
        repr(result)
        == "2640         0.00\n2890     -1044.31\n5410       464.25\n2990      6250.00\n6000         0.00\n1630     -6240.00\n1930     -6250.00\n8423         0.00\n1650       145.00\n2614       -24.78\n2645        24.78\n4535       275.31\n4598      -275.31\n6910       275.31\n3740        -0.25\n2098    853044.04\n2099   -408634.15\n6250       150.00\ndtype: float64"
    )


def test_get_GL_transaction(content):
    df_gl = generate_general_ledger(content)
    result = get_GL_transaction(df_gl, "5")
    assert (
        repr(result)
        == "2990   -6250.0\n6000    6250.0\n1630    6250.0\n1930    6250.0\n8423   -6250.0\nName: 5, dtype: float64"
    )


def test_get_IB(content):
    result = get_IB(content)
    assert (
        repr(result)
        == "          IB2023\n1630       -2.00\n1650     1027.00\n1930    23046.95\n1931        0.00\n2081   -25000.00\n2093  -837177.70\n2099   853044.04\n2440        0.00\n2614    -1861.80\n2640        0.00\n2645     1861.80\n2710        0.00\n2731       -1.40\n2890    -8686.89\n2990    -6250.00"
    )


def test_current_saldo(content):
    result = current_saldo(content)
    assert (
        repr(result)
        == "1630     -6242.00\n1650      1172.00\n1930     16796.95\n1931         0.00\n2081    -25000.00\n2093   -837177.70\n2099    444409.89\n2440         0.00\n2614     -1886.58\n2640         0.00\n2645      1886.58\n2710         0.00\n2731        -1.40\n2890     -9731.20\n2990         0.00\n5410       464.25\n6000         0.00\n8423         0.00\n4535       275.31\n4598      -275.31\n6910       275.31\n3740        -0.25\n2098    853044.04\n6250       150.00\ndtype: float64"
    )
