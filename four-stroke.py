# Imports
import re, datetime, pytz
import search_file, extract_files, read_csv
from pathlib import Path


# Input the date of previous close
def get_prev_date(prev_date_str = None):
    if not prev_date_str:
        ist = pytz.timezone('Asia/Calcutta')
        prev_date_obj = datetime.datetime.date(datetime.datetime.now(ist))
        # prev_date_str = prev_date_obj.strftime("%d%m%Y")
    else:
        # Make a datetime object out of date string given as argument
        prev_date_obj = datetime.datetime.strptime(prev_date_str, "%d-%m-%Y")

    weekday = False
    while not weekday:
        if prev_date_obj.weekday() > 4:
            prev_date_obj = prev_date_obj - datetime.timedelta(days=1)
        # It's a weekday... yay!
        else:
            prev_date_str = prev_date_obj.strftime("%d%m%Y")
            weekday = True
    
    
    return prev_date_str
    

while True:
    index_type = input('Please select one of the index:\n1. Nifty Fifty\n2. Bank Nifty\n0. Exit\nEnter your choice: ')
    if index_type == '0':
        exit(0)
    elif index_type not in ['1', '2']:
        print('Please select a valid option!\n')
    else: 
        break

print()

while True:
    prev_date_str = input('Please enter the previous close date of future. Else, hit enter to choose today as previous close date (empty input): ')
    prev_date_str = prev_date_str.strip()
    if prev_date_str == '':
        prev_date_str = get_prev_date()
        break
    elif re.match('^\d{2}-\d{2}-\d{4}$', prev_date_str):
        prev_date_str = get_prev_date(prev_date_str)
        break
    else:
        print('Please re-enter the end date in dd-mm-yyyy format!')



# Chock if the file is present in data, archive, or downloads, and import if needed
file_names = ['op'+prev_date_str+'.csv', 'fo'+prev_date_str+'.csv']
print('Searching for the csv in data/ folder...')
if search_file.search_file(file_names[0], 'data') == False or search_file.search_file(file_names[1], 'data') == False:
    print('Option and/or future file(s) is not present in data/ folder')
    print('Searching for the archive in archive/ folder...')

    zipfile_name = 'fo'+prev_date_str+'.zip'
    if search_file.search_file(zipfile_name, 'archive') == False:
        print('Zipfile is not present in archive/ folder')
        print('Searching for the archive in download/ folder...')

        downloads_path = str(Path.home() / "Downloads")
        if search_file.search_file(zipfile_name, downloads_path) == False:
            print('Zipfile is not present in downloads folder')
            print('Please download the zip file with name ' + zipfile_name + ' from NSE website')
            exit(0)
        else:
            extract_files.extract(zipname = zipfile_name, file_names = file_names, copy_from_downloads = True)
            print('Copied zipfile from downloads/ to archives/ and extracted the csv files from archives/ folder to data/ folder')

    else:
        extract_files.extract(zipname = zipfile_name, file_names = file_names)
        print('Extracted the csv files from archives/ folder to data/ folder')
else:
    print('Option and Future files found in data folder, proceeding to process')


print('\n\n')
# Read the previous close of the month's future 
prev_date_month = prev_date_str[2:4]
index_name = 'NIFTY     ' if index_type == '1' else 'BANKNIFTY '
constraints = {'SYMBOL    ': index_name}
fut_close_price = read_csv.read_index_data(filename = 'data/'+file_names[1], constraints = constraints, fields = ['CLOSE_PRICE', 'EXP_DATE  '])
# print(fut_close_price)
fut_close_price = fut_close_price[0]
fut_close_price.pop('EXP_DATE  ')

if 'error' in fut_close_price.keys():
    print('Error reading the futures file')
    exit(0)
fut_close_price = float(list(fut_close_price.values())[-1])

# print(fut_close_price)

# Find the nearest ITM call and put
step_size = 50 if index_type == '1' else 100

itm_ce = (fut_close_price // step_size) * step_size
itm_pe = itm_ce + step_size

# Read highs and lows of the ITM CE and PE
index_name = 'NIFTY     ' if index_type == '1' else 'BANKNIFTY '
constraints = {'SYMBOL    ': index_name, 'STR_PRICE  ': '000'+str(itm_ce)+'0', 'OPT_TYPE': 'CE      '}
fields = ['HI_PRICE   ', 'LO_PRICE   ', 'EXP_DATE  ']
hl_ce = read_csv.read_index_data(filename = 'data/'+file_names[0], constraints = constraints, fields = fields)
hl_ce = hl_ce[0]


constraints = {'SYMBOL    ': index_name, 'STR_PRICE  ': '000'+str(itm_pe)+'0', 'OPT_TYPE': 'PE      '}
fields = ['HI_PRICE   ', 'LO_PRICE   ', 'EXP_DATE  ']
hl_pe = read_csv.read_index_data(filename = 'data/'+file_names[0], constraints = constraints, fields = fields)
hl_pe = hl_pe[0]

# print(hl_ce, '\n', hl_pe)
# Suggest the action based on the algorithm
print('The previous close of the index future is: ', fut_close_price)
print('Strike price for CE is', itm_ce)
print('Strike price for PE is', itm_pe)
print('Expiry for the call is',hl_ce['EXP_DATE  '])
print('\n')
print('Here are the action points suggested by 4 stroke algorithm, which is expected to work 80\% of the time:')
print('-------------------------------------------------------------------------------------------------------')
print('1. If {ce_strike} CE opens > {ce_high}, buy {ce_strike} CE.\ntarget = 5% and stop loss = 2.5%. Book profit or loss after 5 min!\nNo keeping overnight!\n'.format(ce_strike = itm_ce, ce_high = float(hl_ce['HI_PRICE   '])))
print('2. If {ce_strike} CE opens < {ce_low}, short {ce_strike} CE.\ntarget = 5% and stop loss = 2.5%. Book profit or loss after 5 min!\nNo keeping overnight!\n'.format(ce_strike = itm_ce, ce_low = float(hl_ce['LO_PRICE   '])))
print('3. If {pe_strike} PE opens > {pe_high}, buy {pe_strike} PE.\ntarget = 5% and stop loss = 2.5%. Book profit or loss after 5 min!\nNo keeping overnight!\n'.format(pe_strike = itm_pe, pe_high = float(hl_pe['HI_PRICE   '])))
print('4. If {pe_strike} PE opens < {pe_low}, short {pe_strike} PE.\ntarget = 5% and stop loss = 2.5%. Book profit or loss after 5 min!\nNo keeping overnight!\n'.format(pe_strike = itm_pe, pe_low = float(hl_pe['LO_PRICE   '])))