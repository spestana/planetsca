# PlanetSCA

**PlanetSCA** is an open source python library for mapping snow covered areas
(SCA) from high-resolution PlanetScope images using a Random Forest model. This
package was developed from [original work by Kehan Yang and others](#citations).

This library also include access to a
[pre-trained model](https://huggingface.co/geo-smart/planetsca_models) for
mapping SCA in PlanetScope imagery, and
[sample data](https://huggingface.co/datasets/geo-smart/planetsca_datasets) to
demonstrate the library's functions.

The search and download functions require you to have an account with Planet and
an [API key](https://developers.planet.com/quickstart/apis/#find-your-api-key).

![PyPlanetSCA](https://raw.githubusercontent.com/DSHydro/PyPlanetSCA-Python-Library/main/additional_assets/PyPlanetSCA_Image.png)

## Documentation

Please see the [website](https://dshydro.github.io/planetsca/) for more
information and detailed documentation.

## Installation

Python must already be installed in your current working environment.
Instructions to create a new conda environment from the terminal, or with VENV
in VSCode, are available [here](#setting-up-an-environment).

To install the python package from
[TestPyPi](https://test.pypi.org/project/planetsca/), use:

```bash
pip install --extra-index-url https://test.pypi.org/simple planetsca
```

## Running the code

1. Import planetsca

```
import planetsca as ps
```

2. Search for PlanetScope imagery

```
api_key = '' # your Planet user API key

# Set up a filter to search a specific time range and region, and to avoid cloudy images:
date_range_filter = ps.search.make_date_range_filter("2024-01-14T00:00:00.000Z", "2024-01-17T00:00:00.000Z")
geometry_filter = ps.search.make_geometry_filter_from_bounds([-105.886, 40.519, -105.872, 40.529])
#geometry_filter = ps.search.make_geometry_filter_from_geojson('my_study_area.geojson') # or use a geojson file
cloud_filter = ps.search.make_cloud_cover_filter(0.05)
filter = ps.search.combine_filters([date_range_filter, geometry_filter, cloud_filter])

# search, results are returned as a geopandas.GeoDataFrame
search_results_gdf = ps.search.search(api_key, filter)
```

3. Order and download data

```
# submit an order using image IDs from the search results
id_list = search_results_gdf.id.to_list()
order_url = ps.download.order(api_key, id_list, filter)

# download
ps.download.download(api_key, order_url, out_dirpath='./output_directory')
```

4. Data Preparation Variable Setup

```
#Set up Paths
dir_ROI = ""
dir_raster = ""
dir_ROIraster = ""
dir_samples_root = ""
dir_samples = ""
```

5. Data Preparation Path 1

```
df_train = data_training_existing(dir_samples)
```

6. Data Preparation Path 2

```
data_training_new(dir_ROI, dir_raster, dir_ROIraster, dir_samples_root)
```

7. Model Training Variable Setup

```
#Setup Paths
dir_model = ""
dir_score = ""

#Model Parameters
n_estimators =
max_dpeth =
max_features =
random_state =
n_splits =
n_repeats =
df_train =
```

8. Retrieve the existing SCA model from Hugging Face

```
ps.model_training.retrieve_model(out_direc, file)
```

9. Or train a new model

```
ps.model_training.train_model(dir_model, dir_score, n_estimators, max_depth, max_features, random_state, n_splits, n_repeats, df_train)
```

10. Prediction Evaluation Variable Setup

```
#Set up directory paths of file locations
dir_raster = ""
dir_out = ""
model = ""

nodata_flag = 9
```

11. Prediction Evaluation

```
ps.prediction_evaluation.run_sca_prediction(dir_raster, dir_out, nodata_flag, model)
```

## Setting up an environment

### Setting up a Virtual Environment (VENV) on VSCode

Creating a VENV is recommended for this project as it ensures that there are no
package conflicts and that troubleshooting is much easier. The following
instructions are summarized from
[here](https://code.visualstudio.com/docs/python/environments).

1. Open Command Palette (Ctrl + Shift + P)
2. Select Venv
3. Select Desired Interpreter Path (I use 3.12.2, minimum version is 3.8)
4. Notification should show up on the bottom right corner titled "Creating
   environment (Show logs): Creating venv...
5. The venv is set up and activated if you see " _Python Version_
   (.'venv':venv)"
6. _NOTE_ After setting up a venv once, VScode will automatically start up the
   virtual environment alongside with VScode. There is no need to repeat these
   steps unless you do not see step 5.

### Setting up a conda environment in the terminal

Find detailed instructions
[here](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands).

1. Open a terminal
2. Create a new environment called "planetenv" with python version 3.8 or
   greater: `conda create -n planetenv python=3.9`
3. Activate your new environment: `conda activate planetenv`
4. Install planetsca from pip
   `pip install --extra-index-url https://test.pypi.org/simple planetsca`

To use jupyter notebooks with this conda environment:

1. Activate your new environment: `conda activate planetenv`
2. Install ipykernel: `pip install --user ipykernel`
3. Connect this environment to notebooks:
   `python -m ipykernel install --user --name=planetenv`
4. When you start a jupyter notebook, you can now select the `planetenv`
   environment kernel

## Citations

When using this package, please **cite both the package and the original study
describing the model**:

Citing PlanetSCA:

Citing the original study:

- Yang K., John A., Shean D., Lundquist J.D., Sun Z., Yao F., Todoran S., and
  Cristea N. (2023) High-resolution mapping of snow cover in montane meadows and
  forests using Planet imagery and machine learning. Front. Water 5:1128758.
  doi: [10.3389/frwa.2023.1128758](https://doi.org/10.3389/frwa.2023.1128758)

Other material of interest:

- Code from the original study which was adapted into this library can be found
  [here](https://github.com/KehanGit/High_resolution_snow_cover_mapping).
- A tutorial describing the random forest model in the original study is
  published as a GeoScience Machine Learning Resources and Training (GeoSMART)
  [here](https://geo-smart.github.io/scm_geosmart_use_case/chapters/one.html).

## Contributing

We welcome new contributions, improvements, and bug fixes! New features and
ideas for the package within the scope of snow remote sensing using Planet
imagery are also welcome. Please create an issue to discuss a new feature of bug
fix.

To contribute code addressing new features or bug fixes, follow these steps:

1. Fork the repository
2. Clone your fork to your working environment
   ```bash
   git clone https://github.com/<your_username>/planetsca.git
   ```
3. Go to the repository
   ```bash
   cd planetsca
   ```
4. Install the package
   ```bash
   pip install -e ".[dev]"
   ```
5. Setup pre-commit
   ```bash
   pre-commit install
   ```
6. Create a feature branch with a descriptive name (e.g.
   `bug-fix-planet-api-change`). This command will also switch you to this new
   branch.
   ```bash
   git checkout -b new-branch-name
   ```
7. After making your changes, run pre-commit before pushing those changes to
   your new branch
8. Then submit a pull request (PR) from the feature branch of your fork to
   `DSHydro/planetsca:main`
9. The PR will be reviewed by at least one maintainer, discussed, then merged
