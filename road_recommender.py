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

from helper import calc_row_sum, get_data

# read in data
# file_path = os.path.join('data', 'MR_Route_Data.csv')
# df = pd.read_csv(file_path)
df = get_data('data/route_df.pkl')

def create_model(n_neighbors=20):
    """Return trained NN model"""

    numeric_features = ['route_length','state_prop_rank','user_rating','sinuosity']

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
        # ('scenery', description_transformer, 'scenery_description'),
        # ('drive_enjoyment', description_transformer, 'drive_enjoyment_description'),
        # ('tourism', description_transformer, 'tourism_description'),
        ('state', OneHotEncoder(handle_unknown='ignore'), ['state']),
        ('numeric_features',numeric_transformer, numeric_features),
        ('locale','passthrough',['loc_lat','loc_lon'])
    ])

    engine_pipe = Pipeline([
        ('preprocessor', preprocessor),
        ('nn', NearestNeighbors(n_neighbors=n_neighbors)),#Nearest Neighbors
    ])

    return preprocessor.fit_transform(df), engine_pipe.fit(df)

def get_recommendations(features, model,route_index):
    n=route_index
    dists, indices = model[1].kneighbors(features[n])
    rec_routes = df.loc[indices[0]]
    return rec_routes


if __name__ == '__main__':
    create_model()
