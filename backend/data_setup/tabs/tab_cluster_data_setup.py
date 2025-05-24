import json
import pandas as pd
import datetime
import plotly.express as px
from sklearn.cluster import KMeans
from backend.data_setup.tabs.tab_merchant_data_setup import get_my_transactions_mcc_users



# mcc code
with open("assets/data/mcc_codes.json", "r", encoding="utf-8") as file:
    data = json.load(file)
my_mcc = pd.DataFrame(list(data.items()), columns=["mcc", "merchant_group"])
my_mcc["mcc"] = my_mcc["mcc"].astype(int)
#-----------------prepare data file-----------------------
my_data_file = get_my_transactions_mcc_users() # imported from tab_merchant_data_setup
# add age_group
bins = [0, 25, 35, 45, 55, 65, 200]
labels = ['<25', '26–35', '36–45', '46–55', '56–65', '65+']
my_data_file['age_group'] = pd.cut(my_data_file['current_age'], bins=bins, labels=labels)

print(my_data_file.head())
print(my_data_file.dtypes)

#---------------------------------------------------------

def get_cluster_merchant_group_dropdown():
    my_df = my_mcc
    my_list = sorted(my_df['merchant_group'].unique().tolist())
    my_list.insert(0, 'All Merchant Groups')
    return my_list

