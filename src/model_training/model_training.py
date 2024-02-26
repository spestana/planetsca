def train_model(dir_model, dir_score, n_estimators, max_depth, max_features, random_state):  #Allowing for model paramter changing in function  
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
        model = RandomForestClassifier(n_estimators, max_depth, max_features, random_state)
        # evaluate the model
        cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=1, random_state=1) #Could parametize this as well
        n_accuracy = cross_val_score(model, X, y, scoring='accuracy', cv=cv, n_jobs=-1, error_score='raise')
        n_f1 = cross_val_score(model, X, y, scoring='f1', cv=cv, n_jobs=-1, error_score='raise')
        n_balanced_accuracy = cross_val_score(model, X, y, scoring='balanced_accuracy', cv=cv, n_jobs=-1, error_score='raise')
        
        # report performance
        plt.hist(n_f1)
        print('Repeat times:'.format(), len(n_f1))
        print('F1-score: %.5f (%.5f)' % (n_f1.mean(), n_f1.std()))
        print('Balanced Accuracy: %.5f (%.5f)' % (n_balanced_accuracy.mean(), n_balanced_accuracy.std()))
        print('Accuracy: %.5f (%.5f)' % (n_accuracy.mean(), n_accuracy.std()))

        # fit model with all observations
        model.fit(X,y)
        # save model 
        joblib.dump(model, dir_model)
        # save accuracy 
        scores = pd.DataFrame()
        scores["accuracy"] = n_accuracy
        scores['f1'] = n_f1
        scores['balanced_accuracy'] = n_balanced_accuracy
        scores.to_csv(dir_score, index = False)

        print('Total time used:'.format(), round(time.process_time() - starttime, 1))