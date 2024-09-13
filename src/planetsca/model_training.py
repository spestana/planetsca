import time
import warnings
from typing import Optional

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score

warnings.filterwarnings("ignore")


def train_model(
    df_train: pd.DataFrame,
    new_model_filepath: str,
    new_model_score_filepath: str,
    n_estimators: int = 10,
    max_depth: int = 10,
    max_features: int = 4,
    random_state: Optional[int] = None,
    n_splits: int = 2,
    n_repeats: int = 2,
) -> RandomForestClassifier:
    """
    Trains and creates a new model with custom parameters

    Parameters
    ----------
        df_train: pd.DataFrame
            Dataframe containing training data, must have feature columns 'blue', 'green', 'red', 'nir' and target column 'label'
        new_model_filepath: str
            Filepath to save the model as a joblib file
        new_model_score_filepath: str
            Filepath to save the model score information as a csv file
        n_estimators: int
            Number of trees in the forest, defaults to 10
        max_depth: int
            Maximum depth of the tree, defaults to 10
        max_features: int
            Number of features to consider when looking for the best split, defaults to 4
        random_state: int
            Seed to ensure reproducibility, defaults to None
        n_splits: int
            Number of folds in the cross-validation, defaults to 2
        n_repeats: int
            Number of times cross-validator needs to be repeated, defaults to 2

    Returns
    -------
        model: RandomForestClassifier
            The newly trained model
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
    joblib.dump(model, new_model_filepath)
    print(f"Model saved to {new_model_filepath}")
    # save accuracy
    scores = pd.DataFrame()
    scores["accuracy"] = n_accuracy
    scores["f1"] = n_f1
    scores["balanced_accuracy"] = n_balanced_accuracy
    scores.to_csv(new_model_score_filepath, index=False)
    print(f"Model scores saved to {new_model_score_filepath}")
    print("Total time used:".format(), round(time.process_time() - starttime, 1))

    return model
