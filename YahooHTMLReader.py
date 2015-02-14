import pandas as pd
import os
import time
from datetime import datetime

path = "C:\Users\Dan\Desktop\intraQuarter"

def Key_Stats(gather="Total Debt/Equity (mrq)"):
    statspath = path+'/_KeyStats'
    stock_list = [x[0] for x in os.walk(statspath)] #names of stocks
    df = pd.DataFrame(columns = ['Date',
                                 'Unix',
                                 'Ticker',
                                 'DE Ratio',
                                 'Price',
                                 'stock_p_change',
                                 'SP500',
                                 'sp500_p_change'])

    sp500_df = pd.DataFrame.from_csv("YAHOO-Index_GSPC.csv")#loads SP500 into a dataframe

    ticker_list = []

    for each_dir in stock_list[1:50]: #[0] is the root directory which is unnecessary
        each_file = os.listdir(each_dir) #list of all filenames per stock directory
        ticker = each_dir.split("\\")[-1]
        ticker_list.append(ticker)

        #makes sure starting point is 0 every time we have a new ticker
        starting_stock_value = False
        starting_sp500_value = False
        
        if len(each_file) > 0: #some stock directories don't contain anything
            for file in each_file:
                date_stamp = datetime.strptime(file, '%Y%m%d%H%M%S.html')
                unix_time = time.mktime(date_stamp.timetuple())
                #At this point we have the stock name and timestamp of the file we'll
                #be taking data from
                
                full_file_path = each_dir+'/'+file
                source = open(full_file_path,'r').read()#could be a url
                try:
                    value = float(source.split(gather+':</td><td class="yfnc_tabledata1">')[1].split('</td>')[0])
                    #[1]gets everything after gather link
                    #[0] gets value before the closing tabledata tag
                    
                    #if data was pulled on a weekend, this will subtract 3 days to get us out of the weekend/holidays
                    #kind of rough and can be improved but generally gets the job done.
                    try: 
                        sp500_date = datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d')
                        row = sp500_df[(sp500_df.index == sp500_date)]
                        sp500_value=float(row["Adjusted Close"])
                    except:
                        sp500_date = datetime.fromtimestamp(unix_time-259200).strftime('%Y-%m-%d')
                        row = sp500_df[(sp500_df.index == sp500_date)]
                        sp500_value=float(row["Adjusted Close"])

                    stock_price = float(source.split('</small><big><b>')[1].split('</b></big>')[0])

                    if not starting_stock_value:
                        starting_stock_value = stock_price
                        
                    if not starting_sp500_value:
                        starting_sp500_value = sp500_value

                    stock_p_change = ((stock_price - starting_stock_value) / starting_stock_value)*100.0
                    sp500_p_change = ((sp500_value - starting_sp500_value) / starting_sp500_value)*100.0

                
                    df = df.append({'Date':date_stamp,
                                    'Unix':unix_time,
                                    'Ticker':ticker,
                                    'DE Ratio':value,
                                    'Price':stock_price,
                                    'stock_p_change':stock_p_change,
                                    'SP500':sp500_value,
                                    'sp500_p_change':sp500_p_change},
                                    ignore_index=True)
                except Exception as e:
                    print e#some companies wont have any value
                
                
    save = gather.replace(' ','').replace(')','').replace('(','').replace('/','')+('.csv')
    print(save)
    df.to_csv(save)       
Key_Stats()
