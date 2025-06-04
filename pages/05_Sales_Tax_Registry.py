import os
import streamlit as st
import pandas as pd

cwd = os.getcwd()

try:
    os.mkdir(cwd + "/Data")
except FileExistsError:
    pass

st.set_page_config(page_title="Sales Tax Registry", page_icon="📈")

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

st.sidebar.header("Tax Saving Report")

@st.cache_data
def sale_tax_registry_to_df(sale_tax_registry):
    return pd.read_excel(sale_tax_registry)

@st.cache_data
def download_excel(df):
    df.to_excel(cwd + "/Data/Sales Register.xlsx", index=False)
    with open(cwd + "/Data/Sales Register.xlsx", "rb") as f:
        bytes_data = f.read()
    return bytes_data


col1, = st.columns(1)

with col1:
    sale_registry_file = st.file_uploader("Choose an Sales Registery file", type=["xlsx"])


if sale_registry_file is not None:

    df = sale_tax_registry_to_df(sale_registry_file)


    df = df.rename(columns={'Document Date': 'DocumentDate', 'Document Number': 'DocumentNumber', 'Outlet Code' : 'RecipientCode', 
                            'Outlet Name' : 'RecipientName', 'Outlet GSTIN' : 'RecipientGSTIN', 'HSN Code' : 'HSNCode', 
                            'Item Code' : 'ItemCode', 'Item Name' : 'ItemDescription', 'Qty (EA)' : 'ItemQuantity', 
                            'Taxable Line Amt' : 'TaxableAmount', 'CESS_Tax_Rate' : 'CESSRate', 'CGST_Tax_Value' : 'CGST', 'IGST_Tax_Value' : 'IGST', 'UTGST_Tax_Value' : 'UTGST',
                            'SGST_Tax_Value' : 'SGST', 'CESS_Tax_Value' : 'CESS', 'Net Amt' : 'NetLineAmount', 'Line Amount' : 'GrossTotal'})



    df['HSNDescription'] = df['HSNCode']

    df['RecipientGSTIN'] = df['RecipientGSTIN'].astype(str).replace('nan', '')

    df.loc[df['RecipientGSTIN'] == '', 'RegistrationType'] = 'UnRegistered'
    df.loc[df['RecipientGSTIN'] != '', 'RegistrationType'] = 'Registered'

    df.loc[df['TransactionType'] == 'Sales Invoice', 'TransactionType'] = 'Sale of Goods'

    df['DocumentDate'] = pd.to_datetime(df['DocumentDate'], format='%d/%m/%Y')

    df['DocumentDate'] = df['DocumentDate'].dt.strftime('%d-%b-%Y')

    df['StateCode_Name'] = '29-Karnataka'

    df['PANNo'] = ''


    df['Basic_Price'] = df['Basic_Price'].astype(float)

    df['BPC'] = df['BPC'].astype(int)

    df['ItemPrice'] = df['Basic_Price'] / df['BPC']

    # print(df['Line Amount'])

    df['ItemTotalDiscount'] = df['Discount Amount'] + df['Dist Discount Amount']

    df['GSTRate'] = df['CGST_Tax_Rate'] + df['SGST_Tax_Rate']

    df['KFCESS'] = 0

    df['DocumentValue'] = 0
    df['InvRoundOffValue'] = 0


    df = df[['TransactionType', 'DocumentDate', 'DocumentNumber', 'DocumentValue',
        'InvRoundOffValue', 'RecipientCode', 'RecipientName',
        'RegistrationType', 'StateCode_Name', 'RecipientGSTIN', 'PANNo',
        'HSNCode', 'HSNDescription', 'ItemCode', 'ItemDescription', 'ItemPrice',
        'ItemQuantity', 'GrossTotal', 'ItemTotalDiscount', 'SubDTMargin',
        'TaxableAmount', 'GSTRate', 'CESSRate', 'CGST', 'SGST', 'UTGST', 'IGST',
        'CESS', 'KFCESS', 'NetLineAmount']]

    for invoice in df['DocumentNumber'].unique():
        df.loc[df['DocumentNumber'] == invoice, 'DocumentValue'] = df[df['DocumentNumber'] == invoice]['NetLineAmount'].sum()
        df['DocumentValue'] = df['DocumentValue'].round()
        document_value = df[df['DocumentNumber'] == invoice]['NetLineAmount'].sum()
        if document_value % 1 < 0.5:
            # print(round(document_value % 1 - 1, 2)) 
            df.loc[df['DocumentNumber'] == invoice, 'InvRoundOffValue'] = round(document_value % 1 - 1, 2)
        else:
            # print(round(1 - document_value % 1, 2)) 
            df.loc[df['DocumentNumber'] == invoice, 'InvRoundOffValue'] = round(1 - document_value % 1, 2)
        # print(document_value % 1)

    st.divider()
    
    if df is not None and not df.empty:
        st.dataframe(df)
    else:
        st.warning("No data available! Please upload a file.")

    st.divider()

    excel_bytes = download_excel(df)

    with open(cwd + "/Data/Sales Register.xlsx", "rb") as file:
        tax_saving_report_dwn_button = st.download_button(
        label="Download Excel File",
        data=excel_bytes,
        file_name="Sales Register.xlsx",
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    # df.to_excel('sales registry.xlsx', index=False)
# print(df.columns)
