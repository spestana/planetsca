def single_image_evaluation(dir_raster, dir_model, dir_out):
    # dir_raster = 'data/download/20180528_181110_1025_3B_AnalyticMS_SR_clip.tif'
    # dir_model = "random_forest_20240116_binary_174K.joblib"
    # dir_out = './data/SCA/'

    model = joblib.load(dir_model)
    nodata_flag = 9
    run_sca_prediction(dir_raster, dir_out, nodata_flag, model)