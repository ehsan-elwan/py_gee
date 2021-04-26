import ee
from helpers import attributes_setter, addNDVI, reducers, state_to_dataframe, state_to_google_drive
from config import connection_config, date_config, export_config, optical_config, asset_config


def mask_clouds(img):
    cloud_shadow_bit_mask = (1 << 3)
    clouds_bit_mask = (1 << 5)
    qa = img.select('pixel_qa')
    mask = qa.bitwiseAnd(cloud_shadow_bit_mask).eq(0).And(qa.bitwiseAnd(clouds_bit_mask).eq(0))
    return img.updateMask(mask)


def reduce_img(img):
    return img.reduceRegions(regions, reducers(ee), 10).filter(
        ee.Filter.notNull(["{}_mean".format(optical_config.get('L8').get('bands')[0])])).map(
        lambda ft: attributes_setter(ft, img, optical_config.get('L8').get('attributes')))


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

L8_collection = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR').filterDate(st_start, st_end).filterBounds(
    regions)
nb_of_rst = L8_collection.size().getInfo()
print("Found {} raster(s) matching search criteria".format(nb_of_rst))
if nb_of_rst > 0:
    L8_collection = L8_collection.map(lambda img: mask_clouds(img))
    L8_collection = L8_collection.map(lambda img: addNDVI(img, ['B5', 'B4']))
    L8_collection = L8_collection.select(optical_config.get('L8').get('bands'))

    stats = L8_collection.map(lambda img: reduce_img(img)).flatten()

    # res = stats.getInfo()
    #
    # df = state_to_dataframe(res, asset_config.get('feature_identifier'), optical_config.get('L8').get('bands'))
    # df.to_csv("Export_L8_{}.csv".format( asset_config.get('asset_name')), index=False)

    state_to_google_drive(stats, export_config.get('output_folder'), 'L8', asset_config.get('asset_name'),
                          export_config.get('running_sleep_time'))
