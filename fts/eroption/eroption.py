
import datetime

import query_op
import query_symbol


if __name__ == '__main__':
    year = datetime.date.year
    month = datetime.date.month
    
    y_m_day = datetime.date.today()    
    day_of_week = y_m_day.isoweekday()
    #Find the next Friday Monday == 1 ... Sunday == 7
    days_left_week = ((12 - day_of_week) % 7)
    exp_day = y_m_day + datetime.timedelta(days_left_week)  
    #get up to a week of symbols
    ticker_symbols = []

    for days in range(days_left_week + 1):
        t_symbols = query_symbol.Earnings().get_symbols(days)
        print t_symbols
        ticker_symbols.extend(t_symbols)
        
    print(ticker_symbols)
    
    candidate_list = []
    for ticker in ticker_symbols:
        query_x = query_op.YQLQuery(ticker)
        close_price_dict = query_x.get_stock(columns=('symbol','LastTradePriceOnly'))
        market_cap_dict = query_x.get_stock(columns=('symbol','MarketCapitalization'))
        stock_close_price = 1.0
        try:
            stock_close_price = close_price_dict['LastTradePriceOnly']
        except:
            stock_close_price = 1.0;
            
        try:
            market_cap = market_cap_dict['MarketCapitalization']
        except:
            market_cap = '1M';

        #option_json = query_x.get_option(exp='2014-05-23')
        option_day_str = exp_day.isoformat()
        option_json = query_x.get_option(exp=option_day_str)
        option_day_str = option_day_str.translate(None,'-')
        option_day_str = option_day_str[2:]
        call_options = []
        put_options = []
        option_exist = option_json.get('option')
        if market_cap.find('B') > 0 and option_exist:
            print ticker, stock_close_price, market_cap
            lower_bound = float(stock_close_price) * 0.8
            upper_bound = float(stock_close_price) * 0.85
            thresh_bound = 0.85
            thresh_hold = 0.002
            for item in option_json['option']:
                #{"symbol":"PETM140621P00055000","type":"P","strikePrice":"55","lastPrice":"0.55","change":"0.29","changeDir":"Up","bid":"NaN","ask":"NaN","vol":"538","openInt":"30"},
                if item['type'] == 'C':
                    call_options.append(item)
                else:
                    put_options.append(item)
                    strike_price = item['strikePrice']
                    last_price = item['lastPrice']
                    strike_sym = item['symbol']
                    #last price is at least 7 cents
                    #only check this week's expiration
                    #strike price is at least 85 percent
                    #and find out several ratio minimum is 0.2 percent
                    if float(last_price) >= 0.07 and strike_sym.find(option_day_str) > 0 and float(strike_price) <= float(stock_close_price) * thresh_bound :
                        ratio = float(last_price) / (float(stock_close_price) - float(strike_price))
                        if ratio > thresh_hold:
                            print ratio, item
                            candidate_list.extend[item]
                    
    print candidate_list

