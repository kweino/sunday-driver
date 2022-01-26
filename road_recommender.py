import gzip
import os

import dill
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, RobustScaler, OneHotEncoder
from spacy.lang.en.stop_words import STOP_WORDS
STOP_WORDS = STOP_WORDS.union({'ll', 've', 'pron'})

from helper import calc_row_sum

# read in data
file_path = os.path.join('data', 'MR_Route_Data.csv')
df = pd.read_csv(file_path)

def create_model(num_neighbors):
    """Return trained NN model"""
    num_neighbors = num_neighbors

    numeric_features = ['route_length','state_prop_rank']#,'scenery_rating','drive_enjoyment_rating','tourism_rating']

    # transformers
    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="mean")), ("scaler", RobustScaler())
    ])

    description_transformer = TfidfVectorizer(stop_words=STOP_WORDS,
                                       ngram_range=(1,2),
                                       min_df=.01)

    engagement_transformer = FunctionTransformer(calc_row_sum)


    # preprocessor & pipe
    preprocessor = ColumnTransformer([
        ('route_engagement',engagement_transformer, ['num_user_reviews','num_users_rode','num_users_want2ride']),
        ('scenery', description_transformer, 'scenery_description'),
        ('drive_enjoyment', description_transformer, 'drive_enjoyment_description'),
        ('tourism', description_transformer, 'tourism_description'),
        ('state', OneHotEncoder(handle_unknown='ignore'), ['state']),
        ('numeric_features',numeric_transformer, numeric_features),
        ('locale','passthrough',['loc_lat','loc_lon'])
    ])

    engine_pipe = Pipeline([
        ('preprocessor', preprocessor),
        ('nn', NearestNeighbors(n_neighbors=num_neighbors)),#Nearest Neighbors
    ])

    return preprocessor.fit_transform(df), engine_pipe.fit(df)

def get_recommendations(features, model,route_index):
    n=route_index
    dists, indices = model[1].kneighbors(features[n])
    rec_routes = df.loc[indices[0]]
    return rec_routes


def preserve_model(model, path_name=None):
    """Preserve ML model to disk using dill."""
    if path_name is None:
        path_name = os.path.join('fraud_detection', 'model',
                                 'ml_model.dill.gz')
    with gzip.open(path_name, 'wb') as f:
        dill.dump(model, f)


def deploy_model(model_path):
    """Return loaded ML model from disk."""
    with gzip.open(model_path, 'rb') as f:
        return dill.load(f)

if __name__ == '__main__':
    model = create_model()
    preserve_model(model)
