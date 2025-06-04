import os
import streamlit as st
import pandas as pd
import numpy as np

def replace_approx_99(value):
    return 1.0 if np.isclose(value, 0.99, atol=0.001) else value

st.set_page_config(page_title="STTS Ledger v/s Sales", page_icon="📈")

st.markdown(
    """
    <style>
    .bordered-col {
        border: 2px solid #000; /* Adjust the border color and width as needed */
        padding: 10px; /* Add some padding inside the border */
        border-radius: 5px; /* Optional: Add rounded corners */
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

@st.cache_data
def download_excel(df, sheet2_dict, df_qty_copy):
    from pprint import pprint

    pprint(sheet2_dict)
    file_path = cwd + "/Data/Distributor-profit.xlsx"

    # Convert values to float where possible
    sheet2_df = pd.DataFrame(list(sheet2_dict.items()), columns=['Category', 'Amount'])
    sheet2_df['Amount'] = pd.to_numeric(sheet2_df['Amount'], errors='coerce')  # Convert numbers properly

    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name="Sales Data", index=False)
        sheet2_df.to_excel(writer, sheet_name="Summary", index=False)
        df_qty_copy.to_excel(writer, sheet_name="Average Sale", index=False)

    with open(file_path, "rb") as f:
        bytes_data = f.read()

    return bytes_data



## Price master
## Sales Data
PRICE_MASTER_FILE = st.file_uploader("Choose a Price Master File (XLSX)", type='xlsx')

if PRICE_MASTER_FILE is not None:
    st.success("File successfully uploaded!")

    # Display a preview of the uploaded file
    master_price_df = master_price_file_to_df(PRICE_MASTER_FILE)
    

SALES_DATA = st.file_uploader("Choose a Sale Data File (XLSX)", type='xlsx')

if SALES_DATA is not None:
    st.success("File successfully uploaded!")

    # Display a preview of the uploaded file
    sales_df = sale_price_file_to_df(SALES_DATA)

col1, col2 = st.columns(2)

    # Add content to the first column
with col1:
    st.header("Income")
    roi_amount = st.text_input('Enter the ROI Amount')

    gwd_brk_lek_amt = st.text_input('Enter the Godown Breakage and Leakage Amount')

    di_amount = st.text_input('Enter the MEPI Amount')

    rd_commission = st.text_input('Enter the RD Commission Amount')

with col2:
        st.header("Expense")
        dist_gwdn_total_exps = st.text_input('Distributor Godown total Expense')

        

        payable_tax_amt = st.text_input('Payable Tax Amount')

if PRICE_MASTER_FILE is not None and SALES_DATA is not None and roi_amount and gwd_brk_lek_amt and di_amount and rd_commission and dist_gwdn_total_exps and payable_tax_amt:
    master_price_df['Net Margin'] = master_price_df['OBP Tax'] - master_price_df['DB P Tax']
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

    
    
    sales_df['FOC'] = sales_df['FOC'].astype(float)
    sales_df['FOC'] = sales_df['FOC'].round(2)

    sales_df.fillna(0, inplace=True)

    sales_df.to_csv(cwd + '/Data/dummy_sale_data.csv', index=False)

    sales_df['Final Promotion']=sales_df['Final Promotion'].apply(lambda x:round(x,2))

    sale_promotion_df = sales_df[['Document Number', 'Document Date', 'Order No', 'Final Promotion']]

    sales_df['FOC'] = sales_df['FOC'].apply(replace_approx_99)

    sales_df["Remark"] = str('')

    for i in range(0, len(sales_df)):
        if sales_df.loc[i]['FOC'] == 1.0:
            sales_df.at[i, 'Remark'] = "FREE"
        elif sales_df.loc[i]['DT Promo'] != 0.0:
            sales_df.at[i, 'Remark'] = 'WS'
        
        if sales_df.loc[i]['SubDTMarginWithTax'] != 0.0:
            sales_df.at[i, 'Remark'] = 'Spoke'
    
    sales_df["Gross Profit"] = float('nan')
    sales_df["Net Profit"] = float('nan')

    for i in range(0, len(sales_df)):
        if sales_df.loc[i]["Remark"] != "FREE":
            filtered_series = master_price_df[master_price_df['Code'] == sales_df.loc[i]['Item Code']]['DM']

            dm_price = filtered_series.astype(float).iloc[0]

            net_margin = master_price_df[master_price_df['Code'] == sales_df.loc[i]['Item Code']]['Net Margin']

            net_margin = net_margin.astype(float).iloc[0]

            sales_df.at[i, "Gross Profit"] = dm_price * float(sales_df.loc[i]['Qty (EA)'])

            sales_df.at[i, "Net Profit"] = net_margin * float(sales_df.loc[i]['Qty (EA)'])

        else:
            sales_df.at[i, "Gross Profit"] = 0

            sales_df.at[i, "Net Profit"] = 0


    st.divider()

    st.dataframe(sales_df)
    col3, col4 = st.columns(2)

        # Add content to the first column
    with col3:
        st.header("Income")
        roi_amount_1 = st.container(border=True)
        roi_amount_1.write("ROI Amount")
        roi_amount_1.write(roi_amount)

        gwd_brk_lek_amt_1 = st.container(border=True)
        gwd_brk_lek_amt_1.write("Godown Breakage Leakage Amount")
        gwd_brk_lek_amt_1.write(gwd_brk_lek_amt)

        di_amount_1 = st.container(border=True)
        di_amount_1.write("Di Amount")
        di_amount_1.write(di_amount)

        rd_commission_1 = st.container(border=True)
        rd_commission_1.write("RD Commission")
        rd_commission_1.write(rd_commission)

    with col4:
        st.header("Expense")
        dist_gwdn_total_exps_1 = st.container(border=True)
        dist_gwdn_total_exps_1.write("Distributor Godown Total Expenses")
        dist_gwdn_total_exps_1.write(dist_gwdn_total_exps)

        dt_promo_1 = st.container(border=True)
        dt_promo_1.write("DT/WS Promotion")
        dt_promo_1.write(round(sales_df['DT Promo'].sum(), 2))

        Spoke_margin_amt_1 = st.container(border=True)
        Spoke_margin_amt_1.write("Spoke Margin Amount")
        Spoke_margin_amt_1.write(round(sales_df['SubDTMarginWithTax'].sum(), 2))

        
        payable_tax_amt_1 = st.container(border=True)
        payable_tax_amt_1.write("Payable Tax Amount")
        payable_tax_amt_1.write(payable_tax_amt)

    

    dt_income = float(roi_amount) + float(gwd_brk_lek_amt) + float(di_amount) + float(rd_commission)

    st.divider()

    profit = sales_df['Gross Profit'].sum() + dt_income

    dt_promo = sales_df['DT Promo'].sum()

    spoke_margin = sales_df['SubDTMarginWithTax'].sum()

    profit = profit - (float(dist_gwdn_total_exps) + float(dt_promo) + float(spoke_margin) + float(payable_tax_amt))

    gross_pro, fin_profit = st.columns(2)

    with gross_pro:
        
        st.header("Gross Profit")
        st.write(round(sales_df['Gross Profit'].sum(), 2))
        

    with fin_profit:
        
        st.header('Final Profit')
        st.write(round(round(profit, 2)))   

    sheet2_dict = {
        'ROI Amount' : roi_amount,
        'Godown Breakage Leakage Amount' : gwd_brk_lek_amt,
        'Di Amount' : di_amount,
        'RD Commission' : rd_commission,
        'Distributor Godown Total Expenses' : dist_gwdn_total_exps,
        'DT/WS Promotion' : round(sales_df['DT Promo'].sum(), 2),
        'Spoke Margin Amount' : round(sales_df['SubDTMarginWithTax'].sum(), 2),
        'Payable Tax Amount' : payable_tax_amt,
        'Gross Profit' : round(sales_df['Gross Profit'].sum(), 2),
        'Final Profit' : round(profit, 2)
    }

    st.divider()

    df_qty = sales_df.groupby(['IPC', 'Item Category', 'HSN Code'])[['Qty (PC)']].sum().reset_index()

    df_qty_copy = df_qty.copy()
    df_qty_copy['Qty%'] = 0

    # Compute Total Quantity
    total_qty = df_qty['Qty (PC)'].sum()

    # Calculate Percentage Contribution per IPC
    for ipc in df_qty['IPC'].unique():
        df_ipc = df_qty[df_qty['IPC'] == ipc]
        total_qty_ipc = df_ipc['Qty (PC)'].sum()
        df_qty_copy.loc[df_qty['IPC'] == ipc, 'Qty%'] = str(round((total_qty_ipc / total_qty) * 100, 2)) + "%"

    st.dataframe(df_qty_copy)

    st.divider()

    excel_bytes = download_excel(sales_df, sheet2_dict, df_qty_copy)

    with open(cwd + "/Data/Distributor-profit.xlsx", "rb") as file:
        tax_saving_report_dwn_button = st.download_button(
        label="Download Excel File",
        data=excel_bytes,
        file_name="Distributor-profit.xlsx",
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )