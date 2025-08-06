import os
import streamlit as st
import pandas as pd

cwd = os.getcwd()

try:
    os.mkdir(cwd + "/Data")
except FileExistsError:
    pass

st.set_page_config(page_title="Tax Saving Report", page_icon="📈")

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
def  purchase_file_to_df(purchase_file):
    return pd.read_excel(purchase_file)

@st.cache_data
def  sales_file_to_df(sale_file):
    return pd.read_excel(sale_file)

@st.cache_data
def download_excel(df):
    df.to_excel(cwd + "/Data/Sales Register.xlsx", index=False)
    with open(cwd + "/Data/Sales Register.xlsx", "rb") as f:
        bytes_data = f.read()
    return bytes_data

col1, col2 = st.columns(2)

with col1:
    purchase_file = st.file_uploader("Choose an Purchase file", type=["xlsx"])
with col2:
    sale_file = st.file_uploader("Choose an Sale file", type=["xlsx"])

if purchase_file is not None and sale_file is not None:
    purchase_df = purchase_file_to_df(purchase_file)
    sale_df = sales_file_to_df(sale_file)

    sale_df['Discount Amount'] = sale_df['Discount Amount'].fillna(0)


    purchase_tax_amount = purchase_df['CGST'].sum() + purchase_df['SGST'].sum() + purchase_df['UTGST'].sum() + purchase_df['IGST'].sum() + purchase_df['CESS'].sum()

    sale_tax_amount = sale_df['Tax Amount'].sum()

    pur_col1, sales_col2 = st.columns(2)

    with pur_col1:
        purchase_container = st.container(border=True)
        purchase_container.write("Purchase Tax Amount Sum")
        purchase_container.write(purchase_tax_amount)

    
    with sales_col2:
        sale_container = st.container(border=True)
        sale_container.write("Sales Tax Amount Sum")
        sale_container.write(sale_tax_amount)

    payable_tax_amount = st.container(border=True)

    left_co, cent_co,last_co = st.columns(3)
    with cent_co:
        payable_tax_amount.write("Payable Tax Amount")
        payable_tax_amount.write(round(sale_tax_amount - purchase_tax_amount, 2))

    discount_percenatge = st.text_input("Enter Discount percentage👇")


    if discount_percenatge != '':
    
        master_price_df_non_gst = sale_df[sale_df['Outlet GSTIN'].isnull()]

        master_price_df_gst = sale_df[sale_df['Outlet GSTIN'].notna()]

        master_price_df_non_gst = master_price_df_non_gst[master_price_df_non_gst['TransactionType'] != 'Sales Return']

        st.subheader(f'Length of data after consider only non-GST {len(master_price_df_non_gst)}')

        
        st.write(f"You entered dicount percentage is : {str(discount_percenatge)}%")

        discount_list = []
        gst_rate_list = []
        for i in range(0, len(master_price_df_non_gst)):
            discount_list.append((master_price_df_non_gst.iloc[i]['Net Amt'] / 100) * float(discount_percenatge))
            gst_rate_list.append(((master_price_df_non_gst.iloc[i]['CGST_Tax_Rate'] + master_price_df_non_gst.iloc[i]['SGST_Tax_Rate'] + master_price_df_non_gst.iloc[i]['CESS_Tax_Rate']) / 100) + 1)

        master_price_df_non_gst['discount'] = discount_list
        master_price_df_non_gst['GST'] = gst_rate_list

        master_price_df_non_gst['SubDTMargin'] = master_price_df_non_gst['discount'] / master_price_df_non_gst['GST']

        master_price_df_non_gst['Tax on SubDTMargin'] = master_price_df_non_gst['discount'] - master_price_df_non_gst['SubDTMargin']

        master_price_df_non_gst['Taxable Line Amt'] = master_price_df_non_gst['Line Amount'] - master_price_df_non_gst['Discount Amount'] - master_price_df_non_gst['Dist Discount Amount'] - master_price_df_non_gst['SubDTMargin']

        taxable_line_amt = master_price_df_non_gst['Taxable Line Amt'].to_list()
        cgst_tax_rate = master_price_df_non_gst['CGST_Tax_Rate'].to_list()

        for i in range(0, len(taxable_line_amt)):
            taxable_line_amt[i] = (taxable_line_amt[i] / 100) * cgst_tax_rate[i]

        master_price_df_non_gst['CGST_Tax_Value'] = taxable_line_amt
        master_price_df_non_gst['SGST_Tax_Value'] = taxable_line_amt

        cess_tax_rate = master_price_df_non_gst['CESS_Tax_Rate'].to_list()
        cess_taxable_line_amt = master_price_df_non_gst['Taxable Line Amt'].to_list()

        for i in range(0, len(cess_taxable_line_amt)):
            cess_taxable_line_amt[i] = (cess_taxable_line_amt[i] / 100) * cess_tax_rate[i]
        
        master_price_df_non_gst['CESS_Tax_Value'] = cess_taxable_line_amt
        
        master_price_df_non_gst['Tax Amount'] = master_price_df_non_gst['CGST_Tax_Value'] + master_price_df_non_gst['SGST_Tax_Value'] + master_price_df_non_gst['CESS_Tax_Value']
        master_price_df_non_gst['Net Amt'] = master_price_df_non_gst['Tax Amount'] + master_price_df_non_gst['Taxable Line Amt']

        
        master_price_df_non_gst = master_price_df_non_gst.drop(columns=['discount', 'GST'], axis=1)


        master_price_df_final = pd.concat([master_price_df_gst, master_price_df_non_gst], axis=0)

        master_price_df_final = master_price_df_final.sort_index()

        total_discount = master_price_df_final['Tax Amount'].sum()

        left_dist_tax, last_dist_tax, final_dist_tax = st.columns(3)

        master_price_df_final['Document Date'] = master_price_df_final['Document Date'].dt.strftime('%d/%m/%Y')

        # SUB_Dt_margin, net amount, CGST, SGST, CESS, taxable line amount
        # master_price_df_final['Document Date'] = master_price_df_final['Document Date'].dt.date
        
        master_price_df_final['SubDTMargin']=master_price_df_final['SubDTMargin'].apply(lambda x:round(x,2))

        master_price_df_final['Taxable Line Amt']=master_price_df_final['Taxable Line Amt'].apply(lambda x:round(x,2))

        master_price_df_final['CGST_Tax_Value']=master_price_df_final['CGST_Tax_Value'].apply(lambda x:round(x,2))

        master_price_df_final['SGST_Tax_Value']=master_price_df_final['SGST_Tax_Value'].apply(lambda x:round(x,2))

        master_price_df_final['CESS_Tax_Value']=master_price_df_final['CESS_Tax_Value'].apply(lambda x:round(x,2))

        master_price_df_final['Tax on SubDTMargin']=master_price_df_final['Tax on SubDTMargin'].apply(lambda x:round(x,2))

        master_price_df_final['Net Amt']=master_price_df_final['Net Amt'].apply(lambda x:round(x,2))

        master_price_df_final['Tax Amount']=master_price_df_final['Tax Amount'].apply(lambda x:round(x,2))

        master_price_df_final['Landed Price']=master_price_df_final['Landed Price'].apply(lambda x:round(x,2))

        master_price_df_final['CouponTotal']=master_price_df_final['CouponTotal'].apply(lambda x:round(x,2))

        st.dataframe(master_price_df_final)

        discount_tax_container = st.container(border=True)
        with left_dist_tax:
            discount_tax_container.write(f"For {discount_percenatge} % the Payable Sales Tax Amount is reduced to :")
            discount_tax_container.write(round(total_discount, 2))

        total_saving_container = st.container(border=True)

        with last_dist_tax:
            total_saving_container.write("Total Payable Tax Amount is : ")
            total_saving_container.write(round(total_discount - purchase_tax_amount, 2))

        total_discount_on_tax = st.container(border=True)
        with final_dist_tax:
            total_discount_on_tax.write("Total Save on payable tax is : ")
            final_dist = round(sale_tax_amount - purchase_tax_amount, 2) - round(total_discount - purchase_tax_amount, 2)
            total_discount_on_tax.write(round(final_dist, 2))

        excel_bytes = download_excel(master_price_df_final)

        with open(cwd + "/Data/Sales Register.xlsx", "rb") as file:
            tax_saving_report_dwn_button = st.download_button(
            label="Download Excel File",
            data=excel_bytes,
            file_name="Sales Register.xlsx",
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )