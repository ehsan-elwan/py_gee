from time import sleep
from datetime import datetime

import ee
import pandas as pd


def attributes_setter(ft, img, attributes):
    for attr in attributes:
        ft = ft.set(attr, img.get(attr))
    ft = ft.set('date', ee.Date(img.get('system:time_start')).format('YYYY-MM-dd'))
    return ft.setGeometry(None)


def addNDVI(img, ndvi_bands):
    return img.addBands(img.normalizedDifference(ndvi_bands).rename('NDVI'))


def state_to_dataframe(state, feature_identifier, bands=[]):
    dict_array = []
    for f in state.get('features'):
        dict_array.append(f['properties'])
    df = pd.DataFrame(dict_array)
    df = df.drop(["{}_count".format(bands[i]) for i in range(1, len(bands))], axis=1)
    return df.sort_values([feature_identifier, 'date'])


def state_to_google_drive(state, gd_folder, mission, asset_name, running_sleep_time):
    task = ee.batch.Export.table.toDrive(state, description="Export_{}_{}".format(mission, asset_name),
                                         folder=gd_folder,
                                         fileFormat='CSV')
    print("Starting Task....")
    task.start()
    while task.status().get('state') == "READY":
        sleep(10)
    print("Task started @: {} ...".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    while task.status().get('state') == "RUNNING":
        sleep(running_sleep_time)
    if task.status().get('state') == "COMPLETED":
        print("Task completed successfully, output stored in:{}".format(task.status().get('destination_uris')))
    else:
        print("Task failed")
    print("Task ended @: {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))


def reducers(gee):
    reducer = gee.Reducer.mean().combine(
        reducer2=gee.Reducer.stdDev(),
        sharedInputs=True
    ).combine(
        reducer2=gee.Reducer.count(),
        sharedInputs=True
    ).combine(
        reducer2=gee.Reducer.variance(),
        sharedInputs=True
    ).combine(
        reducer2=gee.Reducer.kendallsCorrelation(),
        sharedInputs=True
    ).combine(
        reducer2=gee.Reducer.kurtosis(),
        sharedInputs=True
    )

    return reducer
