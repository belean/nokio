import json
from pathlib import Path
import pandas as pd
import numpy as np
from nokio.bokio_import import get_IB, generate_general_ledger
from nokio.transaction import add_transactions


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
