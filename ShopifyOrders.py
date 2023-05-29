def extract_date(date_str):
    from datetime import datetime
    if date_str is None:
        return ""

    try:
        datetime_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
        formatted_date = datetime_obj.strftime("%d/%m/%Y")
    except ValueError:
        formatted_date = ""
    return formatted_date
import pandas as pd

def extract_payment_type(payment_str):
    if 'Cash on Delivery (COD)' in payment_str:
        return 'COD'
    elif 'Razorpay Secure' in payment_str:
        return 'prepaid'
    else:
        return ''
import pandas as pd
import getshopify
import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials
orders = getshopify.get_shopify(30)
new_list = []

for dictionary in orders:
    discount_codes = dictionary.get("discount_codes", [])
    if discount_codes:
        code = discount_codes[0].get("code", "")
        amount = discount_codes[0].get("amount", "")
        discount_type = discount_codes[0].get("type", "")
    else:
        code = ""
        amount = ""
        discount_type = ""
    cust_info=dictionary.get("shipping_address", [])
    if cust_info:
        first_name = cust_info.get("first_name", "")
        last_name = cust_info.get("last_name", "")
        pincode = cust_info.get("zip", "")
        contact = cust_info.get("phone", "")
        state=cust_info.get('province',"")
    else:
        first_name = ""
        last_name = ""
        pincode = ""
        contact=''
        state=''
    awb=dictionary.get("fulfillments", [])
    if awb:
        awd_dict=awb[0].get("tracking_number",'')
    else:
        awd_dict=""
    new_dict = {
        "Order-ID": dictionary["name"],"First-Name":first_name,"Last-Name":last_name,'State':state,"Pincode":pincode,"Contact Number":contact,
        "financial_status": dictionary["financial_status"],
        "fulfillment_status": dictionary["fulfillment_status"],
        "created_at": dictionary["created_at"],
        "Final Price": dictionary['total_price'],
        "discount_codes": code,
        "Discount_Amount": amount,
        "Discount_Type": discount_type,
        "PaymentMode":dictionary['payment_gateway_names'],"AWB":awd_dict
    }
    titles = []
    for application in dictionary.get("discount_applications", []):
            if "title" in application:
                titles.append(application["title"])
    new_dict["check_replacement"] = "; ".join(titles)

    new_list.append(new_dict)

df = pd.DataFrame(new_list)
df['payment_type'] = df['PaymentMode'].apply(extract_payment_type)
df['Order Date']=df["created_at"].apply(extract_date)
df['Customer Name']=df['First-Name']+" "+df['Last-Name']
final=df[[ 'Order Date','Order-ID',"Customer Name", 'State','Pincode', 'Contact Number',\
       'financial_status', 'fulfillment_status', 'Final Price',\
       'discount_codes', 'Discount_Amount', 'Discount_Type',
       'AWB', 'check_replacement', 'payment_type']].copy()
final['Contact Number'] = final['Contact Number'].str.replace('+', '').str.strip().astype(str)


# set the scope of the Google Sheets API
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# specify the path to your service account JSON file
creds = ServiceAccountCredentials.from_json_keyfile_name('./emerald-cab-384306-b8566336d0b0.json', scope)

# authenticate with Google
client = gspread.authorize(creds)

gsB2c = client.open('OrdersTracker')
sheetb2c=gsB2c.worksheet('ShopifyData')
sheetb2c.clear()
set_with_dataframe(sheetb2c,final)
