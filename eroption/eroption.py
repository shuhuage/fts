
import datetime

import query_op
import query_symbol


def sortkeypicker(keynames):
    negate = set()
    for i, k in enumerate(keynames):
        if k[:1] == '-':
            keynames[i] = k[1:]
            negate.add(k[1:])
    def getit(adict):
        composite = [adict[k] for k in keynames]
        for i, (k, v) in enumerate(zip(keynames, composite)):
            if k in negate:
                composite[i] = -v
        return composite
    return getit


if __name__ == '__main__':
    year = datetime.date.year
    month = datetime.date.month
    
    y_m_day = datetime.date.today()    
    day_of_week = y_m_day.isoweekday()
    #Find the next Friday Monday == 1 ... Sunday == 7
    days_left_week = ((12 - day_of_week) % 7)
    exp_day = y_m_day + datetime.timedelta(days_left_week)  

    option_day_str = exp_day.isoformat()

    option_day_str_compact = option_day_str.translate(None,'-')
    option_day_str_compact = option_day_str_compact[2:]

    #get up to a week of symbols
    ticker_symbols = []
    candidate_list = []

    for days in range(days_left_week + 1):
        t_symbols = query_symbol.Earnings().get_symbols(days)
        print t_symbols
        ticker_symbols.extend(t_symbols)
        
    
        for ticker in t_symbols:
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

            
            call_options = []
            put_options = []
            #option_json = query_x.get_option(exp='2014-05-23')
            option_json = query_x.get_option(exp=option_day_str)
            option_exist = option_json.get('option')
            if option_exist and market_cap and market_cap.find('B') > 0:
                print ticker, stock_close_price, market_cap
                thresh_bound = 0.85
                thresh_hold = 15
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
                        #and find out ratio over 0.2 percent
                        if float(last_price) >= 0.07 and strike_sym.find(option_day_str_compact) > 0 and float(strike_price) <= float(stock_close_price) * thresh_bound :
                            reward_ratio = float(last_price) * 10000 / float(strike_price)
                            if reward_ratio > thresh_hold:
                                strike_percent = 100-float(strike_price)*100/float(stock_close_price)
                                print int(reward_ratio),  int(strike_percent), item
                                entry = {'date':days,'ratio':int(reward_ratio), 'percent':int(strike_percent), 'symbol':strike_sym, 'strike': strike_price, 'price':last_price}
                                candidate_list.append(entry)
                    
    #print candidate_list
    for entry in candidate_list:
        print entry
    #sort based on date, then percent and then ratio
    print '========'
    sorted_list = sorted(candidate_list, key=sortkeypicker(['date', '-percent', '-ratio']))
    for entry in sorted_list:
        print entry
