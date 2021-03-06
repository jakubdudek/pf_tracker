#from app import cache

def get_costbasis(tr_by_date_df):
    from pandas import DataFrame
    
    symbols = get_symbols(tr_by_date_df)

    basis_df = DataFrame(0.0, index=symbols, columns = ['shares', 'basis', 'realized'])    
    
    # Fill the time series with amount of stock own at each date
    for (date, trans) in tr_by_date_df.iterrows():
        if(trans['trade']=='BUY' or trans['trade']=='SPLIT' or trans['trade']=='DEPOSIT'):
            #news_basis = ((old_basis*old_shares)+(price*new_shares)) / (old_shares+new_shares)
            old_basis = basis_df.loc[trans['symbol'], 'basis']
            old_shares = basis_df.loc[trans['symbol'], 'shares']
            
            new_basis = ((old_basis * old_shares) + (trans['price']*trans['shares']+trans['commission']+trans['fee']))/(old_shares+trans['shares'])
            basis_df.loc[trans['symbol'], 'basis'] = new_basis
            basis_df.loc[trans['symbol'], 'shares'] += trans['shares']
            
        elif(trans['trade'] == 'SELL'):
            basis_df.loc[trans['symbol'], 'shares'] += trans['shares']
            basis_df.loc[trans['symbol'], 'realized'] -= (trans['price']-basis_df.loc[trans['symbol'], 'basis'])*trans['shares']

    #printprint(basis_df)
    return basis_df       

def get_symbols(tr_by_date_df):
    return list(set(tr_by_date_df.symbol))

#@cache.cached(key_prefix='all_comments')
def get_trans(csv_file):
    import pandas as pd
    

    tr_by_date_df=pd.read_csv(csv_file, index_col='date')
    # remove NaN
    tr_by_date_df.fillna(0.0, inplace=True)     
    #convert dates to timeseries
    tr_by_date_df.index=pd.to_datetime(tr_by_date_df.index)

    #get symbols
    #symbols = list(set(tr_by_date_df.Symbol))
    
    #return the dataframe containing all transactions
    return tr_by_date_df


#@cache.cached(key_prefix='all_comments')
def get_cashflow(tr_by_date_df):
     # retrive all deposits and withdrawals
    return (tr_by_date_df[(tr_by_date_df.trade == "DEPOSIT") |  (tr_by_date_df.trade =="WITHDRAWAL")])['shares']

#@cache.cached(key_prefix='all_comments')
def get_index_rates(cashflow_ts, symbols):
    import pandas as pd
    import pandas.io.data as web
    from pandas.tseries.offsets import BDay
    from pandas import DataFrame
    from datetime import date
    #import numpy as np
    
    # invest cashlfows in index (stored in symbols)
    cashflow_ts.asfreq(BDay(), method='pad')
    bdays = pd.date_range(start=cashflow_ts.index[0], end=date.today()-BDay(1), freq=BDay())
    invalid = []
    pf_hist_df={}
    #rate={}
    cumrate={}
    #cumrate2={}
    for symbol in symbols:
        pf_hist_df[symbol]=DataFrame(index=bdays, columns=['shares'])
        
        try:
            quote=web.DataReader(symbol, 'yahoo', cashflow_ts.index[0])
            pf_hist_df[symbol] = pf_hist_df[symbol].join(quote['Close'].asfreq(BDay(), method='pad'), how='outer')
            cumrate[symbol]=(pf_hist_df[symbol]['Close'].pct_change()+1).cumprod()
            cumrate[symbol].fillna(1.0, inplace=True)
        except:
            invalid.append(symbol)
            
    return cumrate, invalid 

#@cache.cached(key_prefix='all_comments')
def get_holdings(tr_by_date_df, symbols):
    import pandas as pd
    from pandas import Series, DataFrame
    from datetime import date
   
    #[tr_by_date_df, symbols]=get_trans(csv_file) 
     
    # Create a time series for each stock 
    holdings_ts_list={}
    holdings_df_list={}
    for symbol in symbols:
        index= tr_by_date_df[tr_by_date_df.symbol == symbol].index.drop_duplicates().order()
 
        if (symbol == 'MYCASH'):
            holdings_ts_list[symbol]=Series(0.0, index=pd.to_datetime(tr_by_date_df.index).drop_duplicates().order())
            holdings_df_list[symbol]=DataFrame(0.0, index=pd.to_datetime(tr_by_date_df.index).drop_duplicates().order(), columns=['shares', 'costbasis'])
        else:        
            holdings_ts_list[symbol]=Series(0.0, index=index)
            holdings_df_list[symbol]=DataFrame(0.0, index=index, columns=['shares', 'price', 'costbasis'])
    
    
    # Fill the time series with amount of stock own at each date
    for (date, trans) in tr_by_date_df.iterrows():
        # if dividend, add to cash, otherwise add to appropriate holding
        if(trans['trade']=='DIVIDEND'):
            holdings_ts_list['MYCASH'][date] += trans['shares']
            holdings_df_list['MYCASH'].loc[date, 'shares'] += trans['shares']
        else:
            holdings_ts_list[trans['symbol']][date] += trans['shares']
            #holdings_df_list[trans['symbol']].loc[date, 'shares'] += trans['shares']
            holdings_df_list[trans['symbol']].loc[date, 'price'] = trans['price']
            
        
        #if a buy or a sell, adjust cash accordingly
        if(trans['trade']=='BUY' or trans['trade']=='SELL'):
            holdings_ts_list['MYCASH'][date] -= trans['shares']*trans['price']
            holdings_ts_list['MYCASH'][date] -= trans['commission']+trans['fee']
            
            holdings_df_list['MYCASH'].loc[date, 'shares'] -= trans['shares']*trans['price']
            holdings_df_list['MYCASH'].loc[date, 'shares'] -= trans['commission']+trans['fee']
                
    
    holdings_ts_list = {i:j.cumsum() for i,j in holdings_ts_list.items()}
    #holdings_df_list = {i:j.cumsum() for i,j in holdings_df_list.items()}
    #holdings_ts_list = {i:round(j, 2) for i,j in holdings_ts_list.items()}
    
    print("returning hodings")

    return holdings_ts_list
   
def get_current_holdings(holdings_ts_list):
    from pandas import DataFrame
    
    holdings_ts_list = {i:j[-1] for i,j in holdings_ts_list.items()}
    #holdings_ts_list = {i:round(j, 2) for i,j in holdings_ts_list.items()}
    #holdings_dict = {i:j for i,j in holdings_ts_list.items() if j != 0.0}
    holdings_dict = {i:j for i,j in holdings_ts_list.items()}
    
    holdings_df=DataFrame(0.0, index=holdings_dict.keys(), columns=['shares', 'price', 'market value'])
    holdings_df['shares']=holdings_dict.values()
    
    return holdings_df
   
#@cache.cached(key_prefix='all_comments')
def get_rates_df(holdings_ts_list, symbols, tr_by_date_df):
    import pandas as pd
    import pandas.io.data as web
    from pandas import DataFrame
    from pandas import Series
    from datetime import date
    from pandas.tseries.offsets import BDay
    import numpy as np
    #from matplotlib.pyplot import *    
      
 
    #[holdings_ts_list, symbols, tr_by_date_df] = get_holdings(csv_file)
    
    bdays = pd.date_range(start=tr_by_date_df.index[0], end=date.today()-BDay(1), freq=BDay())
    
    invalid_symbols = []; 
    
    # Cumulate positions in the time series, pad for all buisness days, 
    # convert to a data frame and merge(join) with yahoo quote.
    pf_hist_df={}
    
    print("about to download quotes...")
    for symbol in symbols:
 
        #holdings_ts_list[symbol]=np.round(holdings_ts_list[symbol],2)
        
        #fill in missing dates and pad data
        holdings_ts_list[symbol]=holdings_ts_list[symbol].asfreq(BDay(), method='pad')
        
        # convert to a data frame
        pf_hist_df[symbol]=DataFrame(holdings_ts_list[symbol], columns=['shares'])
    
        # download prices for all dates.  If cash create a quote of all 1s
        # of the appropriate lenght
        
        
        
        if(symbol == 'MYCASH'):
            quote=DataFrame(1, index=bdays, columns=['Close'])
            # join quote with dataframe of holdings, dates with no holings with inherit nan
            pf_hist_df[symbol] = pf_hist_df[symbol].join(quote['Close'].asfreq(BDay(), method='pad'), how='outer')
            pf_hist_df[symbol].fillna(method='pad', inplace=True)
        else:
            try:
                print("Fetching " + symbol)
                quote=web.DataReader(symbol, 'yahoo', pf_hist_df[symbol].index[0])
                print("done with quotes")
                # join quote with dataframe of holdings, dates with no holings with inherit nan
                pf_hist_df[symbol] = pf_hist_df[symbol].join(quote['Close'].asfreq(BDay(), method='pad'), how='outer')
                pf_hist_df[symbol].fillna(method='pad', inplace=True)
       
            except:
                print(symbol+ " does not exist")
                del(holdings_ts_list[symbol])
                #symbols.remove(symbol)
                invalid_symbols.append(symbol)
                



    for symbol in invalid_symbols:
        symbols.remove(symbol)
 
    # create a table of all symbols and daily values
    history=DataFrame(index=bdays, columns=symbols)
    
    for symbol in symbols:
        history[symbol]=pf_hist_df[symbol]['shares']*pf_hist_df[symbol]['Close']
    
    #replace NaN with 0s
    history.fillna(0.0, inplace=True) 
    
    #sum up portfolio value for each day  
    history['worth']=history.sum(axis=1) 
    
    #add a cashflow column to know when deposits happened
    history['Cashflow']=get_cashflow(tr_by_date_df).asfreq(BDay())
    history['Cashflow'].fillna(0.0, inplace=True)  
    
    #create a yesterday column and add today's cashflow
    history['Yesterday']=history['worth'].shift(1)
    history['Yesterday']=history['Yesterday']+history['Cashflow']
    
    # (t-(y+c))/(y+c) simplifies to t/(y+c)-1
    rate=((history['worth']-history['Yesterday'])/history['Yesterday'])+1
    cumrate=rate.cumprod()

    cumrate.fillna(1.0, inplace=True)

    return history['worth'], Series(cumrate, index=history.index), invalid_symbols
    
#@cache.cached(key_prefix='all_comments')
def df_to_obj_list(df, index_name):
    df=df.reset_index()
    df.rename(columns={'index':index_name}, inplace=True)

    print(df)

    #make list of objects from dataframe, for the datatable, add a row id for identifiaction of delete and modify
    object_list=[]
    for i in range(0, len(df)):
        object_list.append(df.loc[df.index[i]].to_dict())

    #everything needs to be a string for datatable
    object_list_str =  [dict([a, str(x)] for a, x in b.items()) for b in object_list]

    return object_list_str

def get_rates(csv_file):
    tr_by_date_df = get_trans("/Users/jakubdudek/transactions_all.csv")
    symbols = get_symbols(tr_by_date_df)
    holdings_ts_list = get_holdings(tr_by_date_df, symbols)
    [worth, cumrates, invalid] = get_rates_df(holdings_ts_list, symbols, tr_by_date_df)
    current = get_current_holdings(holdings_ts_list)
    return worth, cumrates, invalid, current
    
    
    
    
    
#tr = get_trans("/Users/jakubdudek/transactions_all.csv")
    
        
    
#tr_by_date_df=get_trans("/Users/jakubdudek/transactions_all.csv")
#symbols=get_symbols(tr_by_date_df)
#        
#holdings_ts_list = get_holdings(tr_by_date_df, symbols)
#holdings_df = get_current_holdings(holdings_ts_list)
#        
#cost_basis = get_costbasis(tr_by_date_df)
#holdings_df = holdings_df.join(cost_basis['basis'])
#holdings_df = holdings_df.join(cost_basis['realized'])
#
#holdings_list = df_to_obj_list(holdings_df, 'Ticker')


#np.round(holdings_df, decimals=2)




#symbols=get_symbols(tr_by_date_df)
        
#holdings_ts_list = get_holdings(tr_by_date_df, symbols)
#holdings_df = get_current_holdings(holdings_ts_list)    
    
#cost = get_costbasis(tr_by_date_df)

#[worth, cumrates, invalid, current]=get_rates("/Users/jakubdudek/transactions_all.csv")
