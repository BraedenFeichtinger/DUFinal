from datetime import datetime



def earnings_loss(current_value, purchase_price, no_shares):
    calculate_earning_loss = (current_value - purchase_price) * no_shares
    return calculate_earning_loss



def calculate_stock_value_increases(current_value, purchase_price, no_shares):
    stock_value_increases = [
        (current - purchase) / shares
        for current, purchase, shares in zip(current_value, purchase_price, no_shares)
    ]
    return stock_value_increases



def eastock_yieldloss(current_value, purchase_price):
    percent_yield_loss = (current_value - purchase_price) / purchase_price * 100
    return percent_yield_loss

def yr_gainloss(current_value, purchase_price, purchase_date):
    current_date = datetime.today()
    diff = (current_date - purchase_date).days / 365
    yr = (((current_value - purchase_price) / purchase_price) / (diff)) * 100
    return yr

