import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio import features
from rasterio.enums import MergeAlg
import time
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import joblib
import os
import glob
import typer
import warnings

warnings.filterwarnings("ignore")


def vector_rasterize(dir_vector, dir_raster, dir_out, flag_output):
    vector = gpd.read_file(dir_vector)
    # Get list of geometries for all features in vector file
    geom = [shapes for shapes in vector.geometry]

    # Open example raster
    raster = rasterio.open(dir_raster)

    # reproject vector to raster
    vector = vector.to_crs(raster.crs)

    # create tuples of geometry, value pairs, where value is the attribute value you want to burn
    geom_value = (
        (geom, value) for geom, value in zip(vector.geometry, vector["label"])
    )

    # Rasterize vector using the shape and transform of the raster
    rasterized = features.rasterize(
        geom_value,
        out_shape=raster.shape,
        transform=raster.transform,
        all_touched=True,
        fill=9,  # background value
        merge_alg=MergeAlg.replace,
        dtype=np.float32,
    )

    if flag_output:
        with rasterio.open(
            dir_out,
            "w",
            driver="GTiff",
            transform=raster.transform,
            dtype=rasterio.float32,
            count=1,
            width=raster.width,
            height=raster.height,
        ) as dst:
            dst.write(rasterized, indexes=1)
    return rasterized


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

def everything(
    dir_samples: str,
    dir_model: str,
    dir_score: str,
    n_estimators: int,
    max_depth: int,
    max_features: int,
    random_state: int,
    dir_out: str,
    dir_raster: str,
):
    """
    Perform SCA routine
    """
    flag_rasterize = False
    dir_ROI = ""
    dir_ROIraster = ""
    dir_samples_root = ""

    if flag_rasterize:
        flag_output = True
        # rasterize ROI
        ROI = vector_rasterize(
            dir_vector=dir_ROI,
            dir_raster=dir_raster,
            dir_out=dir_ROIraster,
            flag_output=flag_output,
        )

        # save surface reflectance and lable to csv file
        N_scale = 10000.0
        img = rasterio.open(dir_raster)
        ROI = rasterio.open(dir_ROIraster)
        img_read = img.read() / N_scale
        df_img = pd.DataFrame(img_read.reshape([4, -1]).T)
        df_label = pd.DataFrame(ROI.read().reshape([1, -1]).T)

        df_train = pd.concat([df_img, df_label], axis=1)
        df_train.columns = ["blue", "green", "red", "nir", "label"]
        df_train["ndvi"] = (df_train["nir"] - df_train["red"]) / (
            df_train["nir"] + df_train["red"]
        )
        df_train = df_train[df_train.label != 9]
        df_train.label = np.where(df_train.label > 0, 1, 0)
        dir_samples = dir_samples_root + str(int(len(df_train.index) / 1000)) + "k.csv"
        df_train.to_csv(dir_samples, index=False)
    else:
        df_train = pd.read_csv(dir_samples)

    starttime = time.process_time()
    if True:
        X = df_train[["blue", "green", "red", "nir"]]
        y = df_train["label"]

        # pre-process ndvi value to -1.0 to 1.0; fill nan to finite value
        # X[X['ndvi']< -1.0]['ndvi'] = -1.0
        # X[X['ndvi']> 1.0]['ndvi'] = 1.0
        # X[np.isfinite(X['ndvi']) == False]['ndvi'] = np.nan

        # define the model
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            max_features=max_features,
            random_state=random_state,
        )
        # evaluate the model
        cv = RepeatedStratifiedKFold(
            n_splits=10, n_repeats=1, random_state=1
        )  # Could parametize this as well
        n_accuracy = cross_val_score(
            model, X, y, scoring="accuracy", cv=cv, n_jobs=-1, error_score="raise"
        )
        n_f1 = cross_val_score(
            model, X, y, scoring="f1", cv=cv, n_jobs=-1, error_score="raise"
        )
        n_balanced_accuracy = cross_val_score(
            model,
            X,
            y,
            scoring="balanced_accuracy",
            cv=cv,
            n_jobs=-1,
            error_score="raise",
        )

        # report performance
        plt.hist(n_f1)
        print("Repeat times:".format(), len(n_f1))
        print("F1-score: %.5f (%.5f)" % (n_f1.mean(), n_f1.std()))
        print(
            "Balanced Accuracy: %.5f (%.5f)"
            % (n_balanced_accuracy.mean(), n_balanced_accuracy.std())
        )
        print("Accuracy: %.5f (%.5f)" % (n_accuracy.mean(), n_accuracy.std()))

        # fit model with all observations
        model.fit(X, y)
        # save model
        joblib.dump(model, dir_model)
        # save accuracy
        scores = pd.DataFrame()
        scores["accuracy"] = n_accuracy
        scores["f1"] = n_f1
        scores["balanced_accuracy"] = n_balanced_accuracy
        scores.to_csv(dir_score, index=False)

        print("Total time used:".format(), round(time.process_time() - starttime, 1))

    nodata_flag = 9
    run_sca_prediction(dir_raster, dir_out, nodata_flag, model)
    
def cli():
    typer.run(everything)
