import csv, re

# Connect to file in format 'ind_close_all_<ddmmyyyy>.csv'
def read_index_data(filename, constraints, fields):
    res_list = []
    try: 
        with open(filename) as csvfile:
            csv_dict_reader = csv.DictReader(csvfile)
            for row in csv_dict_reader:
                select = True
                for constraint in constraints.keys():
                    if row[constraint] != constraints[constraint]:
                        # print(type(row[constraint]),row[constraint],'\t\t', constraints[constraint], type(constraints[constraint]))
                        select = False
                        break
                if select:
                    # res_dict[index_name] = index_name
                    # res_dict['Expiry'] = row['EXP_DATE  ']
                    res = {}
                    for field in fields:
                        res[field] = row[field]
                    res_list.append(res)
                    
    # If file is not found, return error
    except(FileNotFoundError): 
        print('File '+ filename + ' not found.')
        res_list = [{'error': True}]
    return res_list 

# Runs only when the file is run from CLI
if __name__ == '__main__':
    print(read_index_data('data/fo01102021.csv', 'NIFTY     ', ['CLOSE_PRICE']))