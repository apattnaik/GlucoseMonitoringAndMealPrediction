from scipy.io import loadmat
from datetime import datetime, timedelta
import csv
import pandas as pd


TIME_MAP_THRESHOLD = timedelta(minutes=10)
TIME_CGM_THRESHOLD = timedelta(minutes=30)
MEAL_THRESHOLD = 1.0
FIX_CGM_WHILE_MAPPING = 0


def parse_mat_data():
    mat_data = loadmat('data/InsulinGlucoseData2_withTimeStr.mat')
    # extract individual values from .mat dictionary
    cgm_data = list(zip(mat_data['numCGM'][0], convert_date_str_to_date_obj(mat_data['dateNumberStr'])))
    insulin_data = list(zip(mat_data['actBolusDelivered'][0], convert_date_str_to_date_obj(mat_data['dateMuBolusStr'])))
    # mapped_cgm_insulin_data = get_data_mapped_by_time(cgm_data, insulin_data)
    mapped_cgm_meal = insulin_to_meal()
    with open('data/cgm_to_meal_start.csv', 'w', newline='', encoding='utf-8') as out:
        csv_out = csv.writer(out)
        csv_out.writerow(['cgm','time_insulin','time_cgm','meal_start','meal'])
        # csv_out.writerow(['cgm', 'insulin', 'insulin_time', 'cgm_time'])
        for row in mapped_cgm_meal:
            csv_out.writerow(row)


def convert_date_str_to_date_obj(date_str_list):
    return [datetime.strptime(date_str, '%d-%b-%Y %H:%M:%S') for date_str in date_str_list]

def get_data_mapped_by_time(cgm_data, insulin_data):
    """
    :return: the format of output is always (cgm_val, insulin_val) for the nearest points in time
    """
    list1, list2 = insulin_data, cgm_data
    mapped_data = []
    progress = 0
    for val1, val1_time in list1:
        min_time_delta = TIME_MAP_THRESHOLD.total_seconds()
        mapped_val2 = None
        mapped_val2_time = None
        for val2, val2_time in list2:
            time_delta = val2_time - val1_time
            if time_delta.total_seconds()>0:
                if time_delta.total_seconds() < min_time_delta:
                    mapped_val2 = val2
                    mapped_val2_time = val2_time
                    min_time_delta = time_delta.total_seconds()
        progress += 1
        if progress % 1000 == 0:
            print("{} values examined".format(progress))
        mapped_data.append((mapped_val2,val1,val1_time,mapped_val2_time))
    return mapped_data




def insulin_to_meal():
    # sorted_data = sorted(mapped_cgm_insulin_data, key=lambda x: x[2])
    # print(sorted_data[2],len(sorted_data))
    data = pd.read_csv('data/cgm_insulin.csv').values
    sorted_data = sorted(data, key=lambda x: x[2])
    mapped_label = []
    i=0
    flag = 0
    while i<len(sorted_data):
        print(i)
        row = sorted_data[i]
        if row[1]>MEAL_THRESHOLD:
            start_time = row[2]
            start_time = datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S')
            end_time = start_time + TIME_CGM_THRESHOLD
            mapped_label.append((row[0], row[2],row[3],1, 0))
            for j in range(i+1,len(sorted_data)):
                if i!=j:
                    X = sorted_data[j][2]
                    if(datetime.strptime(sorted_data[j][2],'%Y-%m-%d %H:%M:%S')>start_time) and (datetime.strptime(sorted_data[j][2],'%Y-%m-%d %H:%M:%S')<=end_time):
                        mapped_label.append((sorted_data[j][0],sorted_data[j][2],sorted_data[j][3],0,1))
                    else:
                        break
            i = j
        else:
            mapped_label.append((row[0],row[2],row[3],0,0))
            i = i+1

    return mapped_label




if __name__ == "__main__":
    parse_mat_data()
