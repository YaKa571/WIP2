import pandas as pd
from backend.data_manager import DataManager
import json
"""
contains data setup for Merchant tab
"""

# Data Files
dm: DataManager = DataManager.get_instance()
my_transactions = dm.df_transactions
# mcc code
with open("assets/data/mcc_codes.json", "r", encoding="utf-8") as file:
    data = json.load(file)
my_mcc = pd.DataFrame(list(data.items()), columns=["mcc_code", "merchant_group"])
my_mcc["mcc_code"] = my_mcc["mcc_code"].astype(int)
# print(my_mcc.head())


def get_most_frequently_used_merchant_group():
    group_return = "group 1"
    count_return = "count 1"
    return group_return, count_return

def get_highest_value_merchant_group():
    group_return = "group 2"
    value_return = "value 2"
    return group_return, value_return