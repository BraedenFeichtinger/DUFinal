from prettytable import PrettyTable
from datetime import datetime, timedelta
from Stock_Functions import earnings_loss, eastock_yieldloss, yr_gainloss,calculate_stock_value_increases
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pyodbc
import requests

table = PrettyTable() 
table2 = PrettyTable()

table2_header = ["Stock", "Share #", "Earnings/Loss","Increase Per Share","Yield/Loss Pct","Yearly Earning/Loss"," NASDAQ Stocks Last Price"] #set up table two outputs 
table2.field_names = table2_header


##create multiple dictionaries within a list to populate the stock info including the extra three required 
#use the datetime function for later calculations 
stock_info = [
    {'stock_symbol': 'GOOGLE', 'number_of_shares': 25, 'purchase_price': 772.88, 'current_value': 941.53, 'purchase_date':datetime(2017,8,1)},
    {'stock_symbol': 'MSFT', 'number_of_shares': 85, 'purchase_price': 56.60, 'current_value': 73.04, 'purchase_date':datetime(2017,8,1)},     
    {'stock_symbol': 'RSD-A', 'number_of_shares': 400, 'purchase_price': 49.58, 'current_value': 55.74, 'purchase_date':datetime(2017,8,1)},       
    {'stock_symbol': 'AIG', 'number_of_shares': 235, 'purchase_price': 54.21, 'current_value': 65.27, 'purchase_date':datetime(2017,8,1)},       
    {'stock_symbol': 'FB', 'number_of_shares': 130, 'purchase_price': 124.31, 'current_value': 175.45, 'purchase_date':datetime(2017,8,1)},
    {'stock_symbol': 'M', 'number_of_shares': 425, 'purchase_price': 30.30, 'current_value': 23.98, 'purchase_date':datetime(2018,1,10)}, 
    {'stock_symbol': 'F', 'number_of_shares': 85, 'purchase_price': 12.58, 'current_value': 10.95, 'purchase_date':datetime(2018,2,17)},        
    {'stock_symbol': 'IBM', 'number_of_shares':80, 'purchase_price': 150.37, 'current_value': 145.30, 'purchase_date':datetime(2018,5,12)},
]



earnings_losses = [] #set up empty earnings loss list to later append the iterated earnings losses per stock
stock_value_increases=[] #set up empty list called stock value increases to append the stock yield percentage increase per stock
stock_value_yieldlosses=[]
yearly_earninglosses=[]  #set up empty list for yearly earnings lost percentage per stock to append in the function later

title_header = "Stock Ownership for Bob Smith"

for stock in stock_info:
    table.add_row([stock['stock_symbol'], stock['number_of_shares'], stock['purchase_price'], stock['current_value'],stock['purchase_date']])
    earning_loss = earnings_loss(stock['current_value'], stock['purchase_price'],stock['number_of_shares']) #call function
    earnings_losses.append(earning_loss) 
    stock_value_increase = calculate_stock_value_increases(
        [stock['current_value']],
        [stock['purchase_price']],
        [stock['number_of_shares']])[0] 
    stock_value_increases.append(stock_value_increase)
    stock_value_yield_loss=eastock_yieldloss(stock['current_value'],stock['purchase_price']) #call function
    stock_value_yieldlosses.append(stock_value_yield_loss)
    yearly_earningloss=yr_gainloss(stock['current_value'],stock['purchase_price'],stock['purchase_date']) #call function
    yearly_earninglosses.append(yearly_earningloss)
    try:
        api_stock_symbol = stock['stock_symbol']
        api_stock_symbol = api_stock_symbol.replace('GOOGLE', 'GOOGL')
        api_stock_symbol = api_stock_symbol.replace('FB', 'Meta')

        alpha_vantage_api_key = 'JLIDO0JIG3SMGS8G'
        alpha_vantage_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={api_stock_symbol}&interval=5min&apikey={alpha_vantage_api_key}"

        response = requests.get(alpha_vantage_url)
        data = response.json()
        time_series = data.get('Time Series (5min)', {})
        
        # Calculate last Friday's date
        today = datetime.today()
        days_ago = (today.weekday() + 3) % 7  # Subtract 1 day to get to Thursday and then 2 days for last Friday
        last_friday = today - timedelta(days=days_ago)
        
        # Find the closest timestamp to last Friday's date
        last_friday_data = None
        for timestamp in time_series:
            timestamp_date = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            if timestamp_date.date() <= last_friday.date():
                last_friday_data = time_series[timestamp]
                break
        
        if last_friday_data:
            last_friday_price = float(last_friday_data.get('1. open', 0))  # Get '1. open' value if available, else use 0
            stock['last_friday_price'] = last_friday_price
        else:
            stock['last_friday_price'] = None
        print(f"No data available for {stock['stock_symbol']} on last Friday.")
    except Exception as e:
        print(f"Error fetching data for {stock['stock_symbol']}: {e}")


  

    table2.title = title_header
    table2.add_row([stock['stock_symbol'],stock['number_of_shares'],f"${earning_loss:.2f}",f"${stock_value_increase:.2f}", f"{stock_value_yield_loss:.2f}%",f"{yearly_earningloss:.2f}%",f"${stock['last_friday_price']:.2f}" if stock['last_friday_price'] is not None else 'Stock Not on NASDAQ'])
print(table)

highest_valuestock_index = stock_value_increases.index(max(stock_value_increases))
smallest_valuestock_index = stock_value_increases.index(min(stock_value_increases))
max_stock_increase=stock_info[highest_valuestock_index]['stock_symbol']
min_stock_increase=stock_info[smallest_valuestock_index]['stock_symbol']

max_value_increaseAMT = stock_value_increases[highest_valuestock_index]

smallest_value_increaseAMT = stock_value_increases[smallest_valuestock_index]

def calculate_yearly_rate(initial_value, final_value, purchase_date, current_date):
    time_delta = (current_date - purchase_date).days / 365.25
    earnings = final_value - initial_value
    rate = (earnings / initial_value) * 100 / time_delta
    return rate, earnings


total_earnings = sum(earnings_losses)
total_yearly_earnings = sum(yearly_earninglosses)
total_initial_investment = sum(stock['purchase_price'] * stock['number_of_shares'] for stock in stock_info)
total_final_value = sum(stock['current_value'] * stock['number_of_shares'] for stock in stock_info)

total_yearly_rate, total_earnings = calculate_yearly_rate(
    total_initial_investment, 
    total_final_value, 
    min(stock['purchase_date'] for stock in stock_info),  # Use the earliest purchase date
    datetime.today()
)




def check(stock_value_increases, value):
    return (all(stock_increase > value for stock_increase in stock_value_increases)) ##for loop to iterate through each stocks value
value = 0 

if (check(stock_value_increases, value)):
    print("All stocks per share have increased.")
    table_output = f"{table2}\n"
    table_output += f"The stock with the highest increase in value in your portfolio on a per-share basis is: {max_stock_increase} at ${max_value_increaseAMT:.2f}\n"
    table_output += f"The stock with least increase in value in your portfolio on a per-share basis is: {min_stock_increase} at ${smallest_value_increaseAMT:.2f}\n"
    table_output+=f"The total yearly earnings/loss rate for all stocks is: {total_yearly_rate:.2f}%\n"
    table_output+=f"The total earnings/loss amount for all stocks is: ${total_earnings:.2f}"
    print(table_output)
   #the elif checks the function and above "if" statement, if the "if" statement fails, that means not all stocks have increased 
elif all(stock_value < 0 for stock_value in stock_value_increases): #to find out if all stocks failed, not both, we add "all" condition to see if all stocks were less than zero
    print("All stocks per share have decreased.")
    table_output = f"{table2}\n"
    table_output += f"The stock with the least amount lossed in value in your portfolio on a per-share basis is: {max_stock_increase} at ${max_value_increaseAMT:.2f}\n"
    table_output += f"The stock with the most amount lossed in value in your portfolio on a per-share basis is: {min_stock_increase} at ${smallest_value_increaseAMT:.2f}\n"
    table_output+=f"The total yearly earnings/loss rate for all stocks is: {total_yearly_rate:.2f}%\n"
    table_output+=f"The total earnings/loss amount for all stocks is: ${total_earnings:.2f}"
    print(table_output)
else: #in the scenario where the "if" condition failed, that means that not all increased. if "elif" failed, that means that not all stocks decreased, therefore we use "else" to confirm this
    print("Stocks both increased and decreased in your portfolio.")
    table_output = f"{table2}\n"
    table_output += f"The stock with the highest increase in value in your portfolio on a per-share basis is: {max_stock_increase} at ${max_value_increaseAMT:.2f}\n"
    table_output += f"The stock with the most amount lossed in value in your portfolio on a per-share basis is: {min_stock_increase} at ${smallest_value_increaseAMT:.2f}\n"
    table_output+=f"The total yearly earnings/loss rate for all stocks is: {total_yearly_rate:.2f}%\n"
    table_output+=f"The total earnings/loss amount for all stocks is: ${total_earnings:.2f}"
    print(table_output)


class Stock:
    def __init__(self, purchase_id, stock_symbol, no_shares, purchase_price, current_value, purchase_date):
        self.purchase_id = purchase_id
        self.stock_symbol = stock_symbol
        self.no_shares = no_shares
        self.purchase_price = purchase_price
        self.current_value = current_value
        self.purchase_date = purchase_date

    def class_earnings_loss(self):
        calculate_earningloss = (self.current_value - self.purchase_price) * self.no_shares
        return calculate_earningloss

    def class_eastock_yieldloss(self):
        percent_yieldloss = ((self.current_value - self.purchase_price) / self.purchase_price) * 100
        return percent_yieldloss

    def class_yr_gainloss(self):
        current_date = datetime.now().date()
        years = (current_date - self.purchase_date).days / 365
        calc = (((self.current_value - self.purchase_price) / self.purchase_price) / years) * 100
        return calc


class Bond(Stock):
    def __init__(self, purchase_id, stock_symbol, no_shares, purchase_price, current_value,purchase_date, coupon, yield_attributes):
        super().__init__(purchase_id, stock_symbol, no_shares, purchase_price, current_value, purchase_date)
        self.coupon = coupon
        self.yield_attributes = yield_attributes


class Investor:
    def __init__(self, investor_id, name, address, phone_number):
        self.investor_id = investor_id
        self.name = name
        self.address = address
        self.phone_number = phone_number


stock_filepath='C:\\Python\\Assignments\\DoneFolder\\Lesson6_Data_Stocks.txt'

bond_filepath='C:\\Python\\Assignments\\DoneFolder\\Lesson6_Data_Bonds.txt'


def read_stock(stock_filepath):
    stock_textfile = []
    with open(stock_filepath, 'r') as file:
        next(file)

        for line in file:
            line = line.strip() ##strip white spaces
            if not line: ##skip any empty lines and continue 
                continue

            elements = line.split(',')
            if len(elements) != 5: ##there is 5 elements in the stocks txt file, if python does not recognize 5 then it is parsed incorrectly throw error
                print(f"Invalid format: {line}")
                continue

            stock_symbol, no_shares, purchase_price, current_value, purchase_date = elements
            purchase_id = len(stock_textfile) + 1  # Generate unique purchase_id since we need to create a value for this 
            no_shares = int(no_shares)
            purchase_price = float(purchase_price)
            current_value = float(current_value)
            purchase_date = datetime.strptime(purchase_date, '%m/%d/%Y').date()

            stock_dict = {  #create stock dictionary to store the txt data into 
                'purchase_id': purchase_id,
                'stock_symbol': stock_symbol,
                'number_of_shares': no_shares,
                'purchase_price': purchase_price,
                'current_value': current_value,
                'purchase_date': purchase_date
            }
            stock_textfile.append(stock_dict)
        return stock_textfile


def read_bond_data(bond_filepath):
    bond_textfile = []
    with open(bond_filepath, 'r') as file:
        # Skip the header line
        next(file) #read next line from file

        for line in file:
            line = line.strip() #strip white spaces
            if not line: #skip possible empty lines
                continue

            elements = line.rsplit(',', maxsplit=7)  # Split from the right side, limiting to 7 splits
            if len(elements) != 7: #there is 7 elemeents in the txt file so we need to make sure its parsed an sliced correctly
                print(f"Invalid format: {line}")
                continue

            # Extract data from each line
            purchase_id = len(bond_textfile) + 1 ##auto increment to make the purchase ID =1 
            stock_symbol = elements[0] 
            no_shares = int(elements[1])
            purchase_price = float(elements[2])
            current_value = float(elements[3])
            purchase_date = datetime.strptime(elements[4], '%m/%d/%Y').date()
            coupon = float(elements[5])
            yield_attributes = float(elements[6])

            # Create a dictionary for each bond and append it to the bond_info list
            bond_dict = {
                'purchase_id': purchase_id,
                'stock_symbol': stock_symbol,
                'number_of_shares': no_shares,
                'purchase_price': purchase_price,
                'current_value': current_value,
                'purchase_date': purchase_date,
                'coupon': coupon,
                'yield_attributes': yield_attributes
            }
            bond_textfile.append(bond_dict)

    return bond_textfile

output_stock_filepath = 'C:\\Python\\Assignments\\DoneFolder\\Stock_ResultFinal.txt'
output_bond_filepath = 'C:\\Python\\Assignments\\DoneFolder\\Bond_ResultFinal.txt'


stock_info = read_stock(stock_filepath)
stock_data = [] ##create list 
for stock in stock_info:
    stock_calcs = Stock(stock['purchase_id'], stock['stock_symbol'], stock['number_of_shares'],
                        stock['purchase_price'], stock['current_value'], stock['purchase_date'])
    stock_row = (stock_calcs.purchase_id, stock_calcs.stock_symbol, stock_calcs.no_shares,
                 stock_calcs.class_earnings_loss(), stock_calcs.class_eastock_yieldloss(), stock_calcs.class_yr_gainloss())
    stock_data.append(stock_row)

# Write stock data to the output file
try:
    with open(output_stock_filepath, 'w') as stock_output_file:
        stock_output_file.write("purchase_id, Stock, Share #, Earnings/Loss, Yield/Loss Pct, Yearly Earning/Loss\n")
        for row in stock_data:
            stock_output_file.write(f"{row[0]}, {row[1]}, {row[2]}, {row[3]:.2f}, {row[4]:.2f}%, {row[5]:.2f}%\n")

    bond_info = read_bond_data(bond_filepath)


except IOError:
    print("Error: Unable to write to the output file.")
except Exception as e:
    print("Error:", str(e))


# Prepare the bond data to be written to a file
bond_data = [] ##create empty list bor bonds to be stored later
for bond in bond_info:
    bond_calcs = Bond(bond['purchase_id'], bond['stock_symbol'], bond['number_of_shares'],
                      bond['purchase_price'], bond['current_value'], bond['purchase_date'],
                      bond['coupon'], bond['yield_attributes'])
    bond_row = (bond_calcs.purchase_id, bond_calcs.stock_symbol, bond_calcs.no_shares, bond_calcs.purchase_price,
                bond_calcs.current_value, bond_calcs.purchase_date, bond_calcs.coupon, bond_calcs.yield_attributes)
    bond_data.append(bond_row)

# Write bond data to the output file, 'w' means write hich is going to generate the txt file
try:
    with open(output_bond_filepath, 'w') as bond_output_file:
        bond_output_file.write("purchase_id, Bond Symbol, No. Shares, Purchase Price, Current Value, Purchase Date, Coupon, Yield\n") #generate header row
        for row in bond_data:
            bond_output_file.write(f"{row[0]}, {row[1]}, {row[2]}, {row[3]:.2f}, {row[4]:.2f}, {row[5]}, {row[6]:.2f}, {row[7]:.2f}\n")
            
except IOError:
    print("Error: Unable to write to the output file.")
except Exception as e:
    print("Error:", str(e))




def load_json(filename):
    with open('C:\Python\Assignments\AllStocks.json', "r") as file:
        data = json.load(file)
    return data




def generate_portfolio_graph(portfolio):
    plt.figure(figsize=(10, 6))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(
        mdates.MonthLocator(interval=3))  # Show every 3 months
    plt.gcf().autofmt_xdate()
    plt.xlabel('Date')
    plt.ylabel('Stock Value')
    plt.title('Stock Value Over Time')

    for investment in portfolio:
        symbol = investment['symbol']
        shares = investment['shares']
        data = investment['data']

        stock_dates = [datetime.strptime(
            entry['Date'], "%d-%b-%y") for entry in data if entry['Symbol'] == symbol]
        stock_values = [entry['Close'] *
                        shares for entry in data if entry['Symbol'] == symbol]

        plt.plot(stock_dates, stock_values, label=symbol)

    plt.legend()
    plt.savefig('portfolio_value_final.png')
    plt.close()


def create_table(connection):
    cursor = connection.cursor()

    # Create SQL table to insert the json files data
    query = """
    CREATE TABLE StockDataJsonData (
        ID INT IDENTITY(1,1) PRIMARY KEY,
        Symbol NVARCHAR(10),
        Date DATE,
        [Open] nvarchar(max),
        High nvarchar(max),
        Low nvarchar(max),
        [Close] nvarchar(max),
        Volume INT
    )
    """

    cursor.execute(query)
    connection.commit()

# Insert data into SQL Server


def insert_data_to_sql(connection, data):
    cursor = connection.cursor()
    query = "INSERT INTO StockDataJsonData (Symbol, Date, [Open], High, Low, [Close], Volume) VALUES (?, ?, ?, ?, ?, ?, ?)"

    for entry in data:
        symbol = entry['Symbol']
        date = entry['Date']
        open_value = str(entry['Open'])
        high = str(entry['High'])
        low = str(entry['Low'])
        close = str(entry['Close'])
        volume = int(entry['Volume'])

        cursor.execute(query, symbol, date, open_value,
                       high, low, close, volume)
    connection.commit()


def main():
    portfolio = [
        {
            "symbol": "GOOGL",
            "shares": 125,
            "data": load_json("portfolio.json")  #
        },
        {
            "symbol": "MSFT",
            "shares": 85,
            "data": load_json("portfolio.json")
        },
        {
            "symbol": "RDS-A",
            "shares": 400,
            "data": load_json("portfolio.json")
        },
        {
            "symbol": "AIG",
            "shares": 235,
            "data": load_json("portfolio.json")
        },
        {
            "symbol": "FB",
            "shares": 150,
            "data": load_json("portfolio.json")
        },
        {
            "symbol": "M",
            "shares": 425,
            "data": load_json("portfolio.json")
        },
        {
            "symbol": "F",
            "shares": 85,
            "data": load_json("portfolio.json")
        },
        {
            "symbol": "M",
            "shares": 80,
            "data": load_json("portfolio.json")
        },
    ]

    server = 'BRAEDEN'
    database = 'AdventureWorks2017'

# Establish the connection
    connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    connection = pyodbc.connect(connection_string)

    # Create the table if it doesn't exist
    create_table(connection)

    for investment in portfolio:
        data = investment['data']
        insert_data_to_sql(connection, data)

    connection.close()

    generate_portfolio_graph(portfolio)


if __name__ == "__main__":
    main()