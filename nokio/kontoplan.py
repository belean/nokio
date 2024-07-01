import pandas as pd
import numpy as np
from pathlib import Path
import json

df = pd.read_excel("data/Kontoplan-BAS-2024.xlsx", skiprows=7, header=1)

df = df.drop(
    [
        "Unnamed: 0",
        "Unnamed: 4",
        "Unnamed: 8",
    ],
    axis=1,
)

df = df.rename(
    columns={
        "Unnamed: 2": "Group_id",
        "Unnamed: 3": "Group_name",
        "Unnamed: 5": "Relevance",
        "Unnamed: 6": "Account_id",
    }
)
df = df.loc[df["Relevance"] == "■"]

df.Account_id = df.Account_id.astype(int)
df = df.drop(columns=df.iloc[:, 0:4])

file_path = Path("data/Bokföring - Bokio - 5592945496/out/5592945496_2023.json")
with open(file_path, "r") as fp:
    content = json.load(fp)


def get_SRU(x):
    return content["KONTO"].get(str(x), {}).get("SRU")


df["SRU"] = df.Account_id.map(lambda x: get_SRU(x))
df = df.rename(columns={"Huvudkonton (xxx0) / Underkonto": "name"})

df = df.set_index("Account_id").drop_duplicates(keep="last")

# Kontogrupper
# In the group id column find the 1 or 2 digit numbers and convert to int
t = (
    df.Group_id.dropna()
    .loc[df.Group_id.dropna().astype(int).map(lambda x: len(str(x)) <= 3)]
    .astype(int)
)

df_acc_group = df.loc[t.index, ["Group_id", "Group_name"]]
df_acc_group["Group_id"] = df_acc_group.Group_id.astype(int)
df_acc_group.to_dict(orient="records")


# indexing

a = [
    [1, 1, 1, 2, 2],
    ["", 10, 11, "", 20],
]

tuples = list(zip(*a))
m_index = pd.MultiIndex.from_tuples(tuples, names=["L1", "L2"])
s = pd.Series(
    [
        "Tillgångar",
        "Immateriella anläggningstillgångar",
        "Patent",
        "Eget kapital och skulder",
        "Eget kapital",
    ],
    index=m_index,
)

# Generate from data frame

# Add a new column with top level group
df_acc_group["L1"] = df_acc_group.Group_id.loc[
    df_acc_group.Group_id.map(lambda x: len(str(x)) == 1)
]
# Forward fill until next valid entry
df_acc_group.L1 = df_acc_group.L1.ffill()

# Add a new column with next level group
df_acc_group["L2"] = df_acc_group.Group_id.loc[
    df_acc_group.Group_id.map(lambda x: len(str(x)) <= 2)
]
# Forward fill until next valid entry
df_acc_group.L2 = df_acc_group.L2.ffill()

# Create new multiindex from dataframe and drop the columns
m_index = pd.MultiIndex.from_frame(df_acc_group[["L1", "L2", "Group_id"]].astype(int))
df_acc_group.drop(columns=["Group_id", "L1", "L2"], inplace=True)

# Set the new index
df_acc_group.index = m_index

# df_acc_group
# df_acc_group.loc[1]
# df_acc_group.loc[2]
# df_acc_group.loc[3]
# df_acc_group.loc[39]
# df_acc_group.loc[3, 39]
# df_acc_group.loc[3, 391]
# df_acc_group.loc[3, 39, 391]


def test():
    data = [
        {(1930, "K"): 3, (2890, "D"): 3},
        {(1930, "D"): 2, (2890, "K"): 1, (2614, "K"): 1},
    ]
    df = pd.DataFrame.from_records(data)
    df.columns = pd.MultiIndex.from_tuples(df.columns, names=["account", "side"])
    df = df.reindex(sorted(df.columns), axis=1)


def convert_trans(trans):
    mytrans = {}
    for item in trans:
        tmp = {}
        for key, val in item[1]["account"].items():
            tmp[(int(key[:-1]), key[-1])] = val
        mytrans[int(item[0])] = tmp

    df = pd.DataFrame.from_records(mytrans)
    df.columns = pd.MultiIndex.from_tuples(df.columns, names=["account", "side"])
    df = df.reindex(sorted(df.columns), axis=1)
    df.index.name = "Transaction"
    return df
