import time
import warnings

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from huggingface_hub import hf_hub_download
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score

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
):
    """
    Trains and creates a model with custom parameters

    Parameters:
        dir_model: String path to save the model
        dir_score: String path to save scores
        n_estimators: Number of trees in the forest
        max_depth: Maximum depth of the tree
        max_features: Number of features to consider when looking for the best split
        random_state: Seed to ensure reproducibility
        n_splits: Number of folds in the cross-validation
        n_repeats: Number of times cross-validator needs to be repeated
        df_train: Dataframe containing training data
    """

    starttime = time.process_time()
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


def retrieve_model(out_direc, file):
    """
    Downloads pre-trained models from hugging faces

    Parameters:
        out_direc: String file path to output directory
        file: String file name to download
    """

    hf_hub_download(
        repo_id="geo-smart/planetsca_models",
        filename=file,
        local_dir=out_direc,
    )
