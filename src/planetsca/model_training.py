import time
import warnings

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score
from huggingface_hub import hf_hub_download 

warnings.filterwarnings("ignore")


def train_model(
    dir_model,
    dir_score,
    n_estimators,
    max_depth,
    max_features,
    random_state,
    n_splits,
    n_repeats,
    df_train,
):  # Allowing for model parameter changing in function
    flag_train = False  # noqa

    # get data
    # dir_model = 'random_forest_20240116_binary_174K.joblib'
    # dir_score = 'random_forest_20240116_binary_174K_scores.csv'
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
            n_splits=n_splits, n_repeats=n_repeats, random_state=random_state
        )
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

def retrieve_model(out_direc):
    hf_hub_download(repo_id="IanChiu333/PyPlanetSCA_Libarary", filename="random_forest_20220513_binary_174K.joblib", local_dir=out_direc)