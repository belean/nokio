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
    convert_trans,
    any_saldo,
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
    assert result.shape == (16, 27)
    assert (
        repr(result.sum())
        == "account  side\n1630     D        18760.00\n         K        18750.00\n1650     D          155.00\n         K           10.00\n1930     D         6250.00\n         K        12500.00\n2098     D       853044.04\n2099     K       853044.04\n2614     D           44.07\n         K           68.85\n2640     D          154.75\n         K          154.75\n2645     D           68.85\n         K           44.07\n2890     K         1044.31\n2990     D        12500.00\n         K         6250.00\n3740     K            0.25\n4535     D          275.31\n4598     K          275.31\n5410     D          464.25\n6000     D        12500.00\n         K        12500.00\n6250     D          150.00\n6910     D          275.31\n8423     D         6250.00\n         K         6250.00\ndtype: float64"
    )


def test_get_GL_accounts(content):
    df_gl = generate_general_ledger(content)
    result = get_GL_accounts(df_gl, 1930)
    assert (
        repr(result)
        == "side              D       K\nTransaction                \n1               NaN     NaN\n2               NaN     NaN\n3               NaN  6250.0\n4               NaN     NaN\n5            6250.0     NaN\n6               NaN  6250.0\n7               NaN     NaN\n8               NaN     NaN\n9               NaN     NaN\n10              NaN     NaN\n11              NaN     NaN\n12              NaN     NaN\n13              NaN     NaN\n14              NaN     NaN\n15              NaN     NaN\n16              NaN     NaN"
    )


def test_get_GL_sum(content):
    df_gl = generate_general_ledger(content)
    result = get_GL_sum(df_gl)
    assert (
        repr(result)
        == "account  side\n1630     D        18760.00\n         K        18750.00\n1650     D          155.00\n         K           10.00\n1930     D         6250.00\n         K        12500.00\n2098     D       853044.04\n2099     K       853044.04\n2614     D           44.07\n         K           68.85\n2640     D          154.75\n         K          154.75\n2645     D           68.85\n         K           44.07\n2890     K         1044.31\n2990     D        12500.00\n         K         6250.00\n3740     K            0.25\n4535     D          275.31\n4598     K          275.31\n5410     D          464.25\n6000     D        12500.00\n         K        12500.00\n6250     D          150.00\n6910     D          275.31\n8423     D         6250.00\n         K         6250.00\ndtype: float64"
    )


def test_get_GL_transaction(content):
    df_gl = generate_general_ledger(content)
    result = get_GL_transaction(df_gl, 5)
    assert (
        repr(result)
        == "account  side\n1630     D       6250.0\n         K       6250.0\n1930     D       6250.0\n2990     K       6250.0\n6000     D       6250.0\n8423     K       6250.0\nName: 5, dtype: float64"
    )


def test_get_IB(content):
    result = get_IB(content)
    assert (
        repr(result)
        == "account 1630    1650      1930 1931     2081  ...    2645 2710 2731     2890    2990\nside       S       S         S    S        S  ...       S    S    S        S       S\nSaldo                                         ...                                   \nIB      -2.0  1027.0  23046.95  0.0 -25000.0  ...  1861.8  0.0 -1.4 -8686.89 -6250.0\n\n[1 rows x 15 columns]"
    )


def test_current_saldo(content):
    result = current_saldo(content)
    assert (
        repr(result)
        == "account\n1630          8.00\n1650       1172.00\n1930      16796.95\n1931          0.00\n2081     -25000.00\n2093    -837177.70\n2098    -853044.04\n2099    1706088.08\n2440          0.00\n2614      -1837.02\n2640          0.00\n2645       1837.02\n2710          0.00\n2731         -1.40\n2890      -7642.58\n2990     -12500.00\n3740          0.25\n4535        275.31\n4598       -275.31\n5410        464.25\n6000          0.00\n6250        150.00\n6910        275.31\n8423          0.00\ndtype: float64"
    )
    result = current_saldo(content, [1630], 0)
    assert repr(result) == "np.float64(-2.0)"
    result = current_saldo(content, [[1630, 1930]], 100)
    assert repr(result) == "account\n1630        8.00\n1930    16796.95\ndtype: float64"
    result = current_saldo(content, ["1630:1930"], 6)
    assert repr(result) == "np.float64(16796.95)"
    result = current_saldo(content, 1930)
    assert repr(result) == "np.float64(16796.95)"


def test_convert_trans():
    trans = """ "V" "11" 20230101 "Boka om årets resultat" 20230505
{
	#TRANS 2098 {} 853044.04
	#TRANS 2099 {} -444409.89
	#TRANS 2099 {} -408634.15
}"""
    result = convert_trans(trans)
    assert (
        repr(result)
        == "Transaction(date=datetime.date(2023, 1, 1), name='Boka om årets resultat', description=None, recorded_at=datetime.datetime(2023, 5, 5, 0, 0), account={'2098D': 853044.04, '2099K': 853044.04}, verificate=11, frozen=None)"
    )


def test_any_saldo(content):
    result = any_saldo(content, 1630, 0)
    assert repr(result) == "np.float64(-2.0)"
    result = any_saldo(content, 1630, 100)
    assert repr(result) == "np.float64(8.0)"
    result = any_saldo(content, 1930, 6)
    assert repr(result) == "np.float64(16796.95)"
    result = any_saldo(content, 1930)
    assert repr(result) == "np.float64(16796.95)"
