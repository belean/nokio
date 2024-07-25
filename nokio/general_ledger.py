import json
from pathlib import Path
import pandas as pd
import numpy as np
from nokio.bokio_import import get_IB, generate_general_ledger
from nokio.transaction import add_transactions, calculate_transaction_balance


def calculate(df_gl: pd.DataFrame, brand: list = None):
    """Calculate the result after freezing the year"""
    gl_brand = {
        "asset": (1000, 1999),
        "dept": (2000, 2999),
        "income": (3000, 3999),
        "cost": (4000, 8999),
    }
    result = {}
    for k, a in gl_brand.items():
        tmp = []
        for c in df_gl.index:
            if a[0] <= c <= a[1]:
                tmp.append(c)
        result[k] = float(df_gl.loc[tmp].sum().round(2))
    return result


def run(content, new_content, content_jsonc):
    """df_ib + df_gl + df_new"""
    df_ib = get_IB(content)
    df_gl = generate_general_ledger(content)
    df_new = add_transactions(new_content)
    df_jsonc = add_transactions(content_jsonc)

    # Continue transaction Id in index
    df_new.index = pd.RangeIndex(df_gl.index[-1] + 1, df_gl.index[-1] + 1 + len(df_new))
    df_jsonc.index = pd.RangeIndex(
        df_new.index[-1] + 1, df_new.index[-1] + 1 + len(df_jsonc)
    )

    df = pd.concat([df_ib, df_gl, df_new, df_jsonc])
    df = df.reindex(sorted(df.columns), axis=1)
    if not abs(calculate_transaction_balance(df).sum().round(2)) < 0.49:
        raise RuntimeError("General ledger does not balance")

    def get_df(account, df):
        if str(account)[0] not in ("2", "3"):
            return (
                df.get((account, "S"), pd.Series([], dtype="float64")).sum()
                + df.get((account, "D"), pd.Series([], dtype="float64")).sum()
                - df.get((account, "K"), pd.Series([], dtype="float64")).sum()
            )
        else:
            return (
                (-1) * df.get((account, "S"), pd.Series([], dtype="float64")).sum()
                - df.get((account, "D"), pd.Series([], dtype="float64")).sum()
                + df.get((account, "K"), pd.Series([], dtype="float64")).sum()
            ) * (-1)

    return df.T.groupby(level=0).apply(lambda df_g: get_df(df_g.name, df_g.T))


if __name__ == "__main__":
    file_path = Path("data/Bokföring - Bokio - 5592945496/new_transactions.json")
    with open(file_path, "r") as fp:
        new_content = json.load(fp)

    file_path = Path("data/Bokföring - Bokio - 5592945496/out/5592945496_2023.json")
    with open(file_path, "r") as fp:
        content = json.load(fp)

    run()
