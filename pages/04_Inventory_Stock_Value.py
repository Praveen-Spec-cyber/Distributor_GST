import os
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Invenntory Stock Value", page_icon="📈")

st.markdown(
            """
            <style>
            [data-testid="stElementToolbar"] {
                display: none;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
st.sidebar.header("Invenntory Stock Value")

cwd = os.getcwd()

try:
    os.mkdir(cwd + "/Data")
except FileExistsError:
    pass

@st.cache_data
def  file_to_df_converter(file_name):
    if file_name.name.endswith('.csv'):
        df = pd.read_csv(file_name)
    elif file_name.name.endswith('.xlsx') or file_name.name.endswith('.xls'):
        df = pd.read_excel(file_name)

    return df

## Price master
## Sales Data
PRICE_MASTER_FILE = st.file_uploader("Choose a Price Master File (XLSX)", type=["csv", "xlsx", "xls"])

if PRICE_MASTER_FILE is not None:
    st.success("File successfully uploaded!")

    # Display a preview of the uploaded file
    master_price_df = file_to_df_converter(PRICE_MASTER_FILE)
    st.subheader("Preview of the Master Data:")
    st.dataframe(master_price_df)

INVENTORY_FILE = st.file_uploader("Choose a Inventory Summary By Item File (XLSX)", type=["csv", "xlsx", "xls"])

if INVENTORY_FILE is not None:
    st.success("File successfully uploaded!")

    # Display a preview of the uploaded file
    inventory_df = file_to_df_converter(INVENTORY_FILE)
    st.subheader("Preview of the Inventory Summary By Item Data:")
    st.dataframe(inventory_df)


if PRICE_MASTER_FILE is not None and INVENTORY_FILE is not None:

    inventory_df['AvlStk(PC-1)'] = inventory_df['AvlStk(PC)'].map(lambda x: str(x).split('.')[0])

    inventory_df['BPC'] = inventory_df['BPC'].map(lambda x: (str(x).split("(")[1]).split(")")[0])

    inventory_df['BPC'] = inventory_df['BPC'].astype('int')

    inventory_df['AvlStk(PC-1)'] = inventory_df['AvlStk(PC-1)'].astype('int')

    inventory_df['Bottle(EA)'] = inventory_df['AvlStk(EA)'] - (inventory_df['BPC'] * inventory_df['AvlStk(PC-1)'])

    inventory_df['Bottle(EA)'] = inventory_df['Bottle(EA)'].astype('str')

    inventory_df['AvlStk(PC-1)'] = inventory_df['AvlStk(PC-1)'].astype('str')

    inventory_df['Bottle(EA)'] = inventory_df['Bottle(EA)'].apply(lambda x: '0' + x if len(x) == 1 else x)

    inventory_df['Quantity CS/EA'] = inventory_df['AvlStk(PC-1)'] + "." + inventory_df['Bottle(EA)']

    inventory_df['Quantity CS/EA'] = inventory_df['Quantity CS/EA'].astype('float')

    inventory_df["Stock Value"] = float('nan')

    count = 0

    for i in range(0, len(inventory_df)):
        filtered_series = master_price_df[master_price_df['Code'] == inventory_df.iloc[i]['ItemCode']]['DB Price']

        if not filtered_series.empty:
            db_price = filtered_series.astype(float).iloc[0]
        else:
            db_price = 0

        stock_value = db_price * inventory_df.iloc[i]['AvlStk(EA)']

        inventory_df.at[i, "Stock Value"] = stock_value



    st.divider()

    st.dataframe(inventory_df)