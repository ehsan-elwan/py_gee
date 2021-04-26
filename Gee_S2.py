import ee
from helpers import attributes_setter, addNDVI, reducers, state_to_dataframe, state_to_google_drive
from config import connection_config, date_config, export_config, optical_config, asset_config


def mask_clouds(img):
    shadow = img.select('SCL').eq(3)
    mask = img.select('MSK_CLDPRB').lt(5).Or(shadow).eq(1)
    return img.updateMask(mask)


def reduce_img(img):
    return img.reduceRegions(regions, reducers(ee), 10).filter(
        ee.Filter.notNull(["{}_mean".format(optical_config.get('S2').get('bands')[0])])).map(
        lambda ft: attributes_setter(ft, img, optical_config.get('S2').get('attributes')))


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

S2_collection = ee.ImageCollection('COPERNICUS/S2_SR').filterDate(st_start, st_end).filterBounds(
    regions)
nb_of_rst = S2_collection.size().getInfo()
print("Found {} raster(s) matching search criteria".format(nb_of_rst))
if nb_of_rst > 0:
    S2_collection = S2_collection.map(lambda img: mask_clouds(img))
    S2_collection = S2_collection.map(lambda img: addNDVI(img, ['B8', 'B4']))
    S2_collection = S2_collection.select(optical_config.get('S2').get('bands'))

    stats = S2_collection.map(lambda img: reduce_img(img)).flatten()

    # res = stats.getInfo()
    #
    # df = state_to_dataframe(res, asset_config.get('feature_identifier'), optical_config.get('S2').get('bands'))
    # df.to_csv("Export_S2_{}.csv".format( asset_config.get('asset_name')), index=False)

    state_to_google_drive(stats, export_config.get('output_folder'), 'S2', asset_config.get('asset_name'),
                          export_config.get('running_sleep_time'))
