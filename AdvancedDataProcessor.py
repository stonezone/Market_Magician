# AdvancedDataProcessor.py

# AdvancedDataProcessor.py

import logging
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from typing import Callable, Union, List
import tensorflow as tf
import spacy
from joblib import Parallel, delayed
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:

    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.scaler = StandardScaler()

    def preprocess(self, data: pd.DataFrame, columns: Union[str, List[str]]) -> pd.DataFrame:
        preprocessed_data = data.copy()
        preprocessed_data[columns] = self.scaler.fit_transform(preprocessed_data[columns])
        return preprocessed_data

    def sentiment_analysis(self, texts: List[str], pipeline: Callable = None, n_jobs: int = -1) -> List[float]:
        if not pipeline:
            pipeline = self.nlp
        results = Parallel(n_jobs=n_jobs)(delayed(pipeline)(text) for text in texts)
        sentiment_scores = [doc.sentiment for doc in results]
        return sentiment_scores

    def train_regression_model(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2) -> Pipeline:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
        pipeline = Pipeline([('scaler', StandardScaler()), ('model', LinearRegression())])
        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        logger.info(f"Mean Squared Error: {mse}")

        return pipeline

    def model_selection(self, X: pd.DataFrame, y: pd.Series, models: List[Callable], param_grid: dict, scoring: str = 'neg_mean_squared_error', n_jobs: int = -1) -> Pipeline:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        grid_search = GridSearchCV(estimator=models, param_grid=param_grid, scoring=scoring, cv=5, n_jobs=n_jobs)
        grid_search.fit(X_train, y_train)

        best_model = grid_search.best_estimator_
        logger.info(f"Best Model: {best_model}")

        return best_model

    def train_neural_network(self, X: pd.DataFrame, y: pd.Series, model: tf.keras.Model, batch_size: int = 32, epochs: int = 100):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mse'])
        model.fit(X_train, y_train, batch_size=batch_size, epochs=epochs, validation_data=(X_test, y_test))
        return model

    def save_model(self, model, model_name: str, model_type: str = 'tensorflow'):
        if model_type == 'tensorflow':
                        model.save(f"{model_name}.h5")
        else:
                        from joblib import dump
                        dump(model, f"{model_name}.joblib")

        def load_model(self, model_name: str, model_type: str = 'tensorflow'):
                if model_type == 'tensorflow':
                        return tf.keras.models.load_model(f"{model_name}.h5")
                else:
                        from joblib import load
                        return load(f"{model_name}.joblib")

                # Add more data processing and analysis methods as needed

                if __name__ == "__main__":
                 data_processor = DataProcessor()

                # Example usage:
                # 1. Preprocess data
                # 2. Perform sentiment analysis
                # 3. Train a regression model
                # 4. Perform model selection
                # 5. Train a neural network
                # 6. Save and load a model
            
