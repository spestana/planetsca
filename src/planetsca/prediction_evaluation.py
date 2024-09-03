import glob
import os

import joblib
import numpy as np
import pandas as pd
import rasterio


def run_sca_prediction(
    planet_path: str,
    model_filepath: str,
    output_dirpath: str = "",
    nodata_flag: int = 9,
) -> None:
    """
    This function predicts binary snow cover from PlanetScope satellite images using a random forest model

    Parameters
    ----------
        planet_path: str
            file path to a single PlanetScope surface reflectance (SR) image, or a directory containing multiple SR images
        model_filepath: str
            file path to a model joblib file
        output_dirpath: str
            the directory where output snow cover images will be stored
        nodata_flag: int
            the value used to represent no data in the predicted snow cover image, default value is 9

    """

    # if output directory is not empty
    if output_dirpath != "":
        # check if the directory already exists
        if not os.path.exists(output_dirpath):
            # create the output directory if it does not already exist
            os.mkdir(output_dirpath)

    # if in_file_path is a directory, then find all images with 'SR' flag, meaning surface reflectance data
    if os.path.isdir(planet_path):
        file_list = glob.glob(planet_path + "/**/*SR*.tif", recursive=True)
    # otherwise we are working with a single planet image
    elif os.path.isfile(planet_path):
        file_list = [planet_path]

    # open the model
    model = joblib.load(model_filepath)

    # open and apply the model to each image in the list
    for f in file_list:
        print("Start to predict:".format(), os.path.basename(f))

        with rasterio.open(f, "r") as ds:
            arr = ds.read()  # read all raster values
            if arr.shape[0] > 4:  # if we have more than 4 bands
                print(
                    "Input image has more than the expected 4 bands (blue, green, red, NIR). \
                This function will continue running using the first four bands in the input image."
                )
                # TODO: use UserWarning, warnings, or logging module to handle messages like this
                arr = arr[:4, :, :]  # use only the first four
                # TODO: add functionality for other cases where we have more than 4 bands (e.g. using NDVI or pseudo-NDSI)

        print("Image dimension:".format(), arr.shape)
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

        # save the resulting SCA image out as a geotiff
        file_out = os.path.join(
            output_dirpath, os.path.splitext(os.path.basename(f))[0] + "_SCA.tif"
        )
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

    return None
