import ee
from helpers import attributes_setter, reducers, state_to_dataframe, state_to_google_drive
from config import connection_config, date_config, radar_config, asset_config, export_config


def reduce_img(img):
    return img.reduceRegions(regions, reducers(ee), 10).filter(
        ee.Filter.expression("VH_count > 0 && angle_count > 0")).map(
        lambda ft: attributes_setter(ft, img, radar_config.get('attributes')))


try:
    credentials = ee.ServiceAccountCredentials(connection_config.get('service_account'),
                                               connection_config.get('json_token'))
    ee.Initialize(credentials)
except Exception as e:
    ee.Authenticate()
    ee.Initialize()

st_start = ee.Date(date_config.get('start'))
st_end = ee.Date(date_config.get('end'))

regions = ee.FeatureCollection(asset_config.get('folder'))
features = regions.toList(regions.size())
regions = ee.FeatureCollection(features)

S1_collection = ee.ImageCollection('COPERNICUS/S1_GRD').filter(ee.Filter.eq('instrumentMode', 'IW')).filter(
    ee.Filter.listContains('transmitterReceiverPolarisation', 'VH')).filter(
    ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')).filterDate(st_start, st_end).filterBounds(
    regions)
nb_of_rst = S1_collection.size().getInfo()
print("Found {} raster(s) matching search criteria".format(nb_of_rst))
if nb_of_rst > 0:
    stats = S1_collection.map(lambda img: reduce_img(img)).flatten()
    #
    # res = stats.getInfo()
    #
    # df = state_to_dataframe(res, asset_config.get('feature_identifier'), radar_config.get('bands'))
    # df.to_csv("Export_S1_{}.csv".format(asset_config.get('asset_name')), index=False)

    state_to_google_drive(stats, export_config.get('output_folder'), 'S1', asset_config.get('asset_name'),
                          export_config.get('running_sleep_time'))
