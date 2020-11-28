from scipy.io import loadmat
from datetime import datetime, timedelta
import csv


TIME_MAP_THRESHOLD = timedelta(minutes=10)
MEAL_THRESHOLD = 1.0
FIX_CGM_WHILE_MAPPING = 0


def parse_mat_data():
    mat_data = loadmat('data/InsulinGlucoseData2_withTimeStr.mat')

    # extract individual values from .mat dictionary
    cgm_data = list(zip(mat_data['numCGM'][0], convert_date_str_to_date_obj(mat_data['dateNumberStr'])))
    insulin_data = list(zip(mat_data['actBolusDelivered'][0], convert_date_str_to_date_obj(mat_data['dateMuBolusStr'])))


    mapped_cgm_insulin_data = get_data_mapped_by_time(cgm_data, insulin_data)
    # mapped_cgm_meal = insulin_to_meal(mapped_cgm_insulin_data)
    #
    # print("Total number of mapped points: {}".format(mapped_cgm_insulin_data.__len__()))
    # with open('data/cgm_to_meal.csv', 'w', newline='', encoding='utf-8') as out:
    #     csv_out = csv.writer(out)
    #     csv_out.writerow(['cgm', 'meal'])
    #     for row in mapped_cgm_meal:
    #         csv_out.writerow(row)


def convert_date_str_to_date_obj(date_str_list):
    return [datetime.strptime(date_str, '%d-%b-%Y %H:%M:%S') for date_str in date_str_list]


def get_data_mapped_by_time(cgm_data, insulin_data):
    """
    :return: the format of output is always (cgm_val, insulin_val) for the nearest points in time
    """
    list1, list2 = insulin_data, cgm_data
    if FIX_CGM_WHILE_MAPPING:
        list1, list2 = cgm_data, insulin_data
    mapped_data = []
    progress = 0
    for val1, val1_time in list1:
        min_time_delta = timedelta(days=365)
        mapped_val2 = None
        for val2, val2_time in list2:
            time_delta = abs(val1_time - val2_time)
            if time_delta < min_time_delta:
                mapped_val2 = val2
                min_time_delta = time_delta
        if min_time_delta < TIME_MAP_THRESHOLD:
            if FIX_CGM_WHILE_MAPPING:
                mapped_data.append((val1, mapped_val2))
            else:
                mapped_data.append((mapped_val2, val1))
        progress += 1
        if progress % 1000 == 0:
            print("{} values examined".format(progress))
    return mapped_data


def insulin_to_meal(mapped_cgm_insulin_data):
    return [(row[0], 1) if row[1] >= MEAL_THRESHOLD else (row[0], 0) for row in mapped_cgm_insulin_data]


if __name__ == "__main__":
    parse_mat_data()
