import joblib
import os
import glob
import rasterio
import pandas as pd
import numpy as np

def run_sca_prediction(dir_raster, dir_out, nodata_flag, model):
    """
    This function predicts binary snow cover for planet satellite images using
    the pre-trained random forest model

    :param dir_raster: the directory or the file of planet images
    :param dir_out: the directory where output snow cover images will be stored
    :param nodata_flag: the value used to represent no data in the predicted snow cover image
    defult value is 9.
    model: the model used to predict snow cover

    """
    # if output directory not exist then creat the output directory
    if not os.path.exists(dir_out):
        os.mkdir(dir_out)

    # if dir_raster is a directory, then find all images with 'SR' flag, meaning surface reflectance data
    if os.path.isdir(dir_raster):
        file_list = glob.glob(dir_raster + "./**/*SR*.tif", recursive=True)
    elif os.path.isfile(dir_raster):
        print("test")
        file_list = [dir_raster]

    for f in file_list:
        print("Start to predict:".format(), os.path.basename(f))

        with rasterio.open(f, "r") as ds:
            arr = ds.read()  # read all raster values
            if arr.shape[0] > 4:  # if we have more than 4 bands
                arr = arr[:4, :, :]  # use only the first four

        print("Image dimension:".format(), arr.shape)  #
        X_img = pd.DataFrame(arr.reshape([4, -1]).T)
        X_img.columns = ["blue", "green", "red", "nir"]

        X_img = X_img / 10000  # scale surface reflectance to 0-1

        X_img["nodata_flag"] = np.where(
            X_img["blue"] == 0, -1, 1
        )  # wherever blue band is zero, set to nodata value of -1

        # run model prediction
        y_img = model.predict(X_img.iloc[:, 0:4])

        out_img = pd.DataFrame()
        out_img["label"] = y_img
        out_img["nodata_flag"] = X_img["nodata_flag"]
        out_img["label"] = np.where(
            out_img["nodata_flag"] == -1, nodata_flag, out_img["label"]
        )  # where we set to -1, set to new nodata_flag value
        # Reshape our classification map
        img_prediction = out_img["label"].to_numpy().reshape(arr[0, :, :].shape)

        file_out = dir_out + os.path.basename(f)[0:-4] + "_SCA.tif"
        print("Save SCA map to: ".format(), file_out)
        with rasterio.open(
            file_out,
            "w",
            driver="GTiff",
            transform=ds.transform,
            dtype=rasterio.uint8,
            count=1,
            crs=ds.crs,
            width=ds.width,
            height=ds.height,
            nodata=nodata_flag,
        ) as dst:
            dst.write(img_prediction, indexes=1, masked=True)


def single_image_evaluation(dir_raster, dir_model, dir_out):
    # dir_raster = 'data/download/20180528_181110_1025_3B_AnalyticMS_SR_clip.tif'
    # dir_model = "random_forest_20240116_binary_174K.joblib"
    # dir_out = './data/SCA/'
    model = joblib.load(dir_model)
    nodata_flag = 9
    run_sca_prediction(dir_raster, dir_out, nodata_flag, model)