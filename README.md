# Model Training
This GitHub repository contains notebooks for training LSTM and CNN models using TensorFlow for time series analysis, along with a simple statistical model.  Additionally, it houses two pre-trained models.
## Structure
*   `tensorflow_main_model_training.ipynb`: This notebook contains the training process for the main_model, which is currently deployed in production.
*   `tensorflow_model_training_cnn.ipynb`: This notebook contains the training process for the cnn_model. While it's more experimental, it has yielded similar results to the main_model.
*   `simple_statistical_model.ipynb`: Here you'll find functions for basic statistical predictions. The statistical insights from this model are utilized in other models.
*   `create_new_data_to_right_format.ipynb`: Although querying data directly from the database in the correct format is the preferred method, this notebook might be useful for formatting data.
*   `train_data_for_main_model.csv`: This CSV file holds the training data used for main_model.
*   `train_data_for_cnn_model.csv`: This CSV file holds the training data used for cnn_model.
*   `visitor_data_with_weather.csv`: Contains visitor data merged with weather data
*   `main_model`: This directory contains the model currently deployed in production.
*   `cnn_model`: A directory housing an experimental CNN model. Feel free to explore its capabilities.
