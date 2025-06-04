import os
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="STTS Ledger v/s Sales", page_icon="📈")

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
st.sidebar.header("STTS Ledger v/s Sales")

cwd = os.getcwd()

try:
    os.mkdir(cwd + "/Data")
except FileExistsError:
    pass

@st.cache_data
def  master_price_file_to_df(purchase_file):
    return pd.read_excel(purchase_file)

@st.cache_data
def  sale_price_file_to_df(purchase_file):
    return pd.read_excel(purchase_file)

## Price master
## Sales Data
PRICE_MASTER_FILE = st.file_uploader("Choose a Price Master File (XLSX)", type='xlsx')

if PRICE_MASTER_FILE is not None:
    st.success("File successfully uploaded!")

    # Display a preview of the uploaded file
    master_price_df = master_price_file_to_df(PRICE_MASTER_FILE)
    st.subheader("Preview of the Master Data:")
    st.dataframe(master_price_df)

SALES_DATA = st.file_uploader("Choose a Sale Data File (XLSX)", type='xlsx')

if SALES_DATA is not None:
    st.success("File successfully uploaded!")

    # Display a preview of the uploaded file
    sales_df = sale_price_file_to_df(SALES_DATA)
    st.subheader("Preview of the Sales Data:")
    st.dataframe(sales_df)



if PRICE_MASTER_FILE is not None and SALES_DATA is not None:
    sales_df[['FOC', 'FOC0', 'FOC1', 'Work', 'Final Promotion', 'FOC Wallet']] = ''
        
    for i in range(0, len(sales_df)):
        if sales_df.loc[i, 'Landed Price'] == 0: 
            try:
                sales_df.loc[i, 'Landed Price'] = float(master_price_df[master_price_df['Code'] == sales_df.iloc[i]['Item Code']]['DB Price'])
            except Exception as e:
                print(e)
        
        sales_df.loc[i, 'FOC'] = float(sales_df.iloc[i]['Net Amt'] / sales_df.iloc[i]['Qty (EA)'])
        
        
        
        if sales_df.loc[i, 'CGST_Tax_Rate'] == 0:
            sales_df.loc[i, 'FOC0'] = sales_df.iloc[i]['Landed Price'] * sales_df.iloc[i]['Qty (EA)']
            sales_df.loc[i, 'Final Promotion'] = sales_df.iloc[i]['Landed Price'] * sales_df.iloc[i]['Qty (EA)']
        
        if type(sales_df.loc[i, 'FOC']) != str:

            if sales_df.loc[i, 'FOC'] >= 0.99 and sales_df.iloc[i]['FOC'] < 1.01:
                sales_df.loc[i, 'FOC1'] = (sales_df.loc[i, 'Landed Price'] * sales_df.loc[i, 'Qty (EA)']) - sales_df.loc[i, 'Net Amt']
                sales_df.loc[i, 'Final Promotion'] = (sales_df.loc[i, 'Landed Price'] * sales_df.loc[i, 'Qty (EA)']) - sales_df.loc[i, 'Net Amt']

            if sales_df.loc[i, "FOC"] < 0.99 and sales_df.loc[i, 'CGST_Tax_Rate'] == 0:
                
                sales_df.loc[i, 'Final Promotion'] = sales_df.loc[i, 'Landed Price'] * sales_df.loc[i, 'Qty (EA)']

            if (sales_df.loc[i, "FOC"] < 0.99 and sales_df.loc[i, 'CGST_Tax_Rate'] != 0) or sales_df.loc[i, 'FOC'] > 1.01:
                sales_df.loc[i, 'Final Promotion'] = sales_df.loc[i, 'Promotion Total'] + sales_df.loc[i, 'CouponTotal']

    
    sales_df.fillna(0, inplace=True)

    sales_df.to_csv(cwd + '/Data/dummy_sale_data.csv', index=False)

    sales_df['Final Promotion']=sales_df['Final Promotion'].apply(lambda x:round(x,2))

    sale_promotion_df = sales_df[['Document Number', 'Document Date', 'Order No', 'Final Promotion']]

    st.divider()

    st.dataframe(sales_df)

    st.divider()

    st.dataframe(sale_promotion_df)

    writer = pd.ExcelWriter(cwd + "/Data/promotion_results.xlsx", engine = 'xlsxwriter')
    sales_df.to_excel(writer, sheet_name = 'sales_data')
    sale_promotion_df.to_excel(writer, sheet_name = 'sale_promotion')
    writer.close()

    with open(cwd + "/Data/promotion_results.xlsx", "rb") as file:
        btn = st.download_button(
                label="Download Excel File",
                data=file,
                file_name="promotion_result.xlsx",
                mime="text/xlsx"
            )

    