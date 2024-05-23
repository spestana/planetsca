import glob
import os

import joblib
import numpy as np
import pandas as pd
import rasterio


def run_sca_prediction(dir_raster, dir_out, nodata_flag, model):
    """
    This function predicts binary snow cover for planet satellite images using
    the pre-trained random forest model

    :param dir_raster: the directory or the file of planet images
    :param dir_out: the directory where output snow cover images will be stored
    :param nodata_flag: the value used to represent no data in the predicted snow cover image
    default value is 9.
    model: the model used to predict snow cover

    """
    # if output directory not exist then creat the output directory
    if not os.path.exists(dir_out):
        os.mkdir(dir_out)

    # if dir_raster is a directory, then find all images with 'SR' flag, meaning surface reflectance data
    if os.path.isdir(dir_raster):
        file_list = glob.glob(dir_raster + "./**/*SR*.tif", recursive=True)
    elif os.path.isfile(dir_raster):
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


def run_sca_prediction_band(f_raster, file_out, nodata_flag, model):
    ndvi_out = (
        os.path.dirname(file_out) + "/" + os.path.basename(file_out)[0:-8] + "_NDVI.tif"
    )
    if not os.path.exists(ndvi_out):
        print(ndvi_out)
        print("Start to predict:".format(), os.path.basename(f_raster))

        with rasterio.open(f_raster, "r") as ds:
            arr = ds.read()  # read all raster values

        print("Image dimension:".format(), arr.shape)  #
        X_img = pd.DataFrame(arr.reshape([4, -1]).T)
        X_img = X_img / 10000  # scale surface reflectance to 0-1
        X_img.columns = ["blue", "green", "red", "nir"]
        # model.fit(X,y)
        y_img = model.predict(X_img)

        X_img["ndvi"] = (X_img["nir"] - X_img["red"]) / (X_img["nir"] + X_img["red"])
        X_img[X_img["ndvi"] < -1.0]["ndvi"] = -1.0
        X_img[X_img["ndvi"] > 1.0]["ndvi"] = 1.0
        X_img["ndvi"] = np.where(
            np.isfinite(X_img["ndvi"]), X_img["ndvi"], 0
        )  # fill nan by NA

        X_img["nodata_flag"] = np.where(X_img["blue"] == 0, -1, 1)
        X_img["ndvi_nan"] = (X_img["nir"] - X_img["red"]) / (
            X_img["nir"] + X_img["red"]
        )

        out_img = pd.DataFrame()
        out_img["label"] = y_img
        out_img["ndvi"] = (X_img.nir - X_img.red) / (X_img.nir + X_img.red)
        out_img["label"] = np.where(
            X_img["nodata_flag"] == -1, np.nan, out_img["label"]
        )
        out_img["label"] = np.where(
            np.isnan(X_img["ndvi_nan"]), np.nan, out_img["label"]
        )

        # Reshape our classification map
        img_prediction = out_img["label"].to_numpy().reshape(arr[0, :, :].shape)
        img_ndvi = out_img["ndvi"].to_numpy().reshape(arr[0, :, :].shape)

        # save image to file_out

        with rasterio.open(
            file_out,
            "w",
            driver="GTiff",
            transform=ds.transform,
            dtype=rasterio.float32,
            count=1,
            crs=ds.crs,
            width=ds.width,
            height=ds.height,
        ) as dst:
            dst.write(img_prediction, indexes=1)

        with rasterio.open(
            ndvi_out,
            "w",
            driver="GTiff",
            transform=ds.transform,
            dtype=rasterio.float32,
            count=1,
            crs=ds.crs,
            width=ds.width,
            height=ds.height,
        ) as dst:
            dst.write(img_ndvi, indexes=1)


def run_sca_prediction_fusion(dir_raster, dir_out, nodata_flag, model):
    for f in glob.glob(dir_raster + "/*.tif", recursive=True):
        file_out = dir_out + "/" + os.path.basename(f)[0:-4] + "_SCA.tif"
        ndvi_out = dir_out + "/" + os.path.basename(f)[0:-4] + "_NDVI.tif"
        # print(file_out)
        # if file exist, next
        if os.path.exists(file_out):
            print(os.path.basename(f) + " SCA exist!")
        else:
            print("Start to predict:".format(), os.path.basename(f))

        with rasterio.open(f, "r") as ds:
            arr = ds.read()  # read all raster values

        print("Image dimension:".format(), arr.shape)  #
        X_img = pd.DataFrame(arr.reshape([4, -1]).T)
        X_img = X_img / 10000  # scale surface reflectance to 0-1
        X_img.columns = ["blue", "green", "red", "nir"]

        # model.fit(X,y)
        y_img = model.predict(X_img)
        X_img["nodata_flag"] = np.where(X_img["blue"] == 0, -1, 1)

        out_img = pd.DataFrame()
        out_img["label"] = y_img
        out_img["ndvi"] = (X_img.nir - X_img.red) / (X_img.nir + X_img.red)
        out_img["nodata_flag"] = X_img["nodata_flag"]
        out_img["label"] = np.where(
            out_img["nodata_flag"] == -1, np.nan, out_img["label"]
        )
        # Reshape our classification map
        img_prediction = out_img["label"].to_numpy().reshape(arr[0, :, :].shape)
        img_ndvi = out_img["ndvi"].to_numpy().reshape(arr[0, :, :].shape)

        # save image to file_out

        with rasterio.open(
            file_out,
            "w",
            driver="GTiff",
            transform=ds.transform,
            dtype=rasterio.float32,
            count=1,
            crs=ds.crs,
            width=ds.width,
            height=ds.height,
        ) as dst:
            dst.write(img_prediction, indexes=1)

        with rasterio.open(
            ndvi_out,
            "w",
            driver="GTiff",
            transform=ds.transform,
            dtype=rasterio.float32,
            count=1,
            crs=ds.crs,
            width=ds.width,
            height=ds.height,
        ) as dst:
            dst.write(img_ndvi, indexes=1)


# run model prediction
def run_sca_prediction_meadows(dir_raster, dir_out, nodata_flag, model):
    subfolders = [f.path for f in os.scandir(dir_raster) if f.is_dir()]
    ids = [x.split("/")[-1] for x in subfolders]
    for i in range(len(ids)):
        if not os.path.exists(dir_out + ids[i]):
            os.makedirs(dir_out + ids[i])

        for f in glob.glob(dir_raster + ids[i] + "/./**/*SR*.tif", recursive=True):
            file_out = dir_out + ids[i] + "/" + os.path.basename(f)[0:-4] + "_SCA.tif"
            ndvi_out = dir_out + ids[i] + "/" + os.path.basename(f)[0:-4] + "_NDVI.tif"
            print(file_out)
            # if file exist, next
            if os.path.exists(file_out):
                print(os.path.basename(f) + " SCA exist!")
            else:
                print("Start to predict:".format(), os.path.basename(f))

                with rasterio.open(f, "r") as ds:
                    arr = ds.read()  # read all raster values

                print("Image dimension:".format(), arr.shape)  #
                X_img = pd.DataFrame(arr.reshape([4, -1]).T)
                X_img = X_img / 10000  # scale surface reflectance to 0-1
                X_img.columns = ["blue", "green", "red", "nir"]

                # model.fit(X,y)
                y_img = model.predict(X_img)
                X_img["nodata_flag"] = np.where(X_img["blue"] == 0, -1, 1)

                out_img = pd.DataFrame()
                out_img["label"] = y_img
                out_img["ndvi"] = (X_img.nir - X_img.red) / (X_img.nir + X_img.red)
                out_img["nodata_flag"] = X_img["nodata_flag"]
                out_img["label"] = np.where(
                    out_img["nodata_flag"] == -1, np.nan, out_img["label"]
                )
                # Reshape our classification map
                img_prediction = out_img["label"].to_numpy().reshape(arr[0, :, :].shape)
                img_ndvi = out_img["ndvi"].to_numpy().reshape(arr[0, :, :].shape)

                # save image to file_out

                with rasterio.open(
                    file_out,
                    "w",
                    driver="GTiff",
                    transform=ds.transform,
                    dtype=rasterio.float32,
                    count=1,
                    crs=ds.crs,
                    width=ds.width,
                    height=ds.height,
                ) as dst:
                    dst.write(img_prediction, indexes=1)

                with rasterio.open(
                    ndvi_out,
                    "w",
                    driver="GTiff",
                    transform=ds.transform,
                    dtype=rasterio.float32,
                    count=1,
                    crs=ds.crs,
                    width=ds.width,
                    height=ds.height,
                ) as dst:
                    dst.write(img_ndvi, indexes=1)


def single_image_evaluation(dir_raster, dir_model, dir_out):
    # dir_raster = 'data/download/20180528_181110_1025_3B_AnalyticMS_SR_clip.tif'
    # dir_model = "random_forest_20240116_binary_174K.joblib"
    # dir_out = './data/SCA/'
    model = joblib.load(dir_model)
    nodata_flag = 9
    run_sca_prediction(dir_raster, dir_out, nodata_flag, model)
