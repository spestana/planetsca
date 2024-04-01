import time
import pandas as pd
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import joblib
import warnings
warnings.filterwarnings('ignore')


def train_model(dir_model, dir_score, n_estimators, max_depth, max_features, random_state, df_train):  #Allowing for model paramter changing in function  
    flag_train = False

    # get data 
    # dir_model = 'random_forest_20240116_binary_174K.joblib'
    # dir_score = 'random_forest_20240116_binary_174K_scores.csv'
    starttime = time.process_time()
    if True:
        X = df_train[['blue', 'green','red','nir']]
        y = df_train['label']
        
        # pre-process ndvi value to -1.0 to 1.0; fill nan to finite value 
        # X[X['ndvi']< -1.0]['ndvi'] = -1.0
        # X[X['ndvi']> 1.0]['ndvi'] = 1.0
        # X[np.isfinite(X['ndvi']) == False]['ndvi'] = np.nan
        # define the model
        model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, max_features=max_features, random_state=random_state)
        # evaluate the model
        cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=1, random_state=1) #Could parametize this as well
        n_accuracy = cross_val_score(model, X, y, scoring='accuracy', cv=cv, n_jobs=-1, error_score='raise')
        n_f1 = cross_val_score(model, X, y, scoring='f1', cv=cv, n_jobs=-1, error_score='raise')
        n_balanced_accuracy = cross_val_score(model, X, y, scoring='balanced_accuracy', cv=cv, n_jobs=-1, error_score='raise')
