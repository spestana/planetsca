import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio import features
from rasterio.enums import MergeAlg
import warnings
warnings.filterwarnings('ignore')

def vector_rasterize(dir_vector, dir_raster, dir_out, flag_output):
    vector = gpd.read_file(dir_vector)
    # Get list of geometries for all features in vector file
    list(vector.geometry)

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

def data_labeling(dir_ROI, dir_raster, dir_ROIraster, dir_samples_root, dir_samples): #Not sure what to call this function
    flag_rasterize = False
    #FILE PATHS CHANGE DEPENDING ON THE PACKAGE - THESE ARE OLD
    # dir_ROI = "./data/ROI/20180528_181110_add_UTM11.shp"
    # dir_raster = "./data/planet/train/20180528_181110_1025_3B_AnalyticMS_SR_clip.tif"
    # dir_ROIraster = './data/ROI/ROI_20180528_181110_add.tif'
    # dir_samples_root = './data/samples/sample_'
    # dir_samples = 'sample_174k.csv'
    if flag_rasterize:
        flag_output = True
        # rasterize ROI
        ROI = vector_rasterize(dir_vector=dir_ROI, dir_raster=dir_raster, dir_out=dir_ROIraster, flag_output = flag_output)
        
        # save surface reflectance and lable to csv file
        N_scale = 10000.0
        img = rasterio.open(dir_raster)
        ROI = rasterio.open(dir_ROIraster)
        img_read = img.read()/N_scale
        df_img = pd.DataFrame(img_read.reshape([4,-1]).T)
        df_label = pd.DataFrame(ROI.read().reshape([1,-1]).T)
        df_train = pd.concat([df_img, df_label], axis = 1)
        df_train.columns = ['blue','green','red','nir','label']
        df_train['ndvi'] = (df_train['nir']-df_train['red'])/(df_train['nir']+df_train['red'])
        df_train = df_train[df_train.label !=9]
        df_train.label = np.where(df_train.label > 0, 1, 0)
        dir_samples = dir_samples_root + str(int(len(df_train.index)/1000)) + 'k.csv'
        df_train.to_csv(dir_samples, index = False)
    else:
        df_train = pd.read_csv(dir_samples)

    return df_train