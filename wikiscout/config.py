import os
import time

# Directory where all scripts should write their output
base_data_dir = '/scratch/wikiscout-data/'
date_format = '%m-%d-%Y'


def get_output_path():
    return base_data_dir + time.strftime(date_format)


def data_dir():
    path = get_output_path()

    if not os.path.exists(path):
        os.makedirs(path)

    return path
