connection_config = dict(service_account='classification@cesbio-gee.iam.gserviceaccount.com',
                         json_token='./gee_token/cesbio-gee-92813d790a84.json')

asset_name = "Italy_100_sample_combined"
asset_config = dict(folder="users/ehsanelwan/" + asset_name, asset_name=asset_name, feature_identifier='FID')

date_config = dict(start='2018-09-01', end='2020-09-01')

optical_config = dict(S2=dict(bands=['B4', 'B8', 'NDVI'],
                              attributes=['MGRS_TILE', 'PRODUCT_ID',
                                          'SENSING_ORBIT_DIRECTION', 'SENSING_ORBIT_NUMBER']),
                      L8=dict(bands=['B4', 'B5', 'NDVI'],
                              attributes=['LANDSAT_ID', 'IMAGE_QUALITY', 'SOLAR_AZIMUTH_ANGLE']))

radar_config = dict(bands=['VH', 'VV', 'angle'],attributes=['orbitProperties_pass', 'relativeOrbitNumber_stop',
                                               'cycleNumber'])

export_config = dict(output_folder='GE_shared', running_sleep_time=60)

# use https://code.earthengine.google.com/   to upload new assets


# var mean_function_selected_band = function(image) {
#   var B2_band = image.select('B2');
#   var B2_band_mean = B2_band.reduceRegion({
#     reducer: ee.Reducer.mean(),
#     geometry: studya_area_geometry,
#     scale: 30
#   }).get('B2');    // added get() call
#   return image.set('B2_mean',B2_band_mean);
# };