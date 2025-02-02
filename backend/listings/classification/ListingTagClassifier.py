import json
import os

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.svm import SVC


class ListingTagClassifier:
    def __init__(self):
        # Define the complete list of tags
        self.ALL_TAGS = [
            "english", "math", "science", "social studies", "history", "music", "biology", "chemistry", 
            "composition", "health", "speech", "physical education", "computer science", "business", "psychology", 
            "spanish", "chinese", "japanese", "russian", "french", "pen", "pencil", "paper", "notebook", "drawing", 
            "art", "textbook", "book", "tech", "computer", "calculator", "marker", "highlighter", 
            "writing", "dry-erase", "laptop", "keyboard", "mouse", "headphones", "airpods", "earbuds", "desktop", 
            "mini-fridge", "furniture", "shelf", "table", "pet", "manga", "silverware", "kitchen", "decoration",
            "chair", "desk", "speaker", "clothing", "backpack", "videogame", "tv", "bag", "entertainment",
            "education", "household", "dorm", "misc", "accessory", "sports", "phone", "tablet", "waterbottle", "cooler"
            ]
        self.vectorizer = TfidfVectorizer(max_df=0.90, lowercase=True, stop_words=["brand","new","used","slightly"])
        self.mlb = MultiLabelBinarizer(classes=self.ALL_TAGS)
        self.model = OneVsRestClassifier(SVC(kernel="linear", probability=True))


        # Set BASE_PATH relative to Django project structure
        self.BASE_PATH = os.path.join(os.path.dirname(__file__), "Saved_Model")

        # Ensure the directory exists
        os.makedirs(self.BASE_PATH, exist_ok=True)

        # Define the full paths for model files
        self.MODEL_PATH = os.path.join(self.BASE_PATH, "tag_classifier.joblib")
        self.VECTORIZER_PATH = os.path.join(self.BASE_PATH, "vectorizer.joblib")
        self.MLB_PATH = os.path.join(self.BASE_PATH, "mlb.joblib")

    def save_model(self):
        """ Saves the trained model for later use.
        """

        # Create base folder if it doesn't exist
        os.makedirs(self.BASE_PATH, exist_ok=True)

        joblib.dump(self.model, os.path.join(self.BASE_PATH, self.MODEL_PATH))
        joblib.dump(self.vectorizer, os.path.join(self.BASE_PATH, self.VECTORIZER_PATH))
        joblib.dump(self.mlb, os.path.join(self.BASE_PATH, self.MLB_PATH))
        print("Model and preprocessors saved successfully.")

    def load_model(self):
        """ Loads the trained model if it exsists.
        """

        try:
            self.model = joblib.load(os.path.join(self.BASE_PATH, self.MODEL_PATH))
            self.vectorizer = joblib.load(
                os.path.join(self.BASE_PATH, self.VECTORIZER_PATH)
            )
            self.mlb = joblib.load(os.path.join(self.BASE_PATH, self.MLB_PATH))

            print(f"Model and preprocessors loaded from '{self.BASE_PATH}/'.")
            return True
        except FileNotFoundError:
            print(f"No saved model found in '{self.BASE_PATH}/'. Train model first.")
            return None, None, None

    def read_listings_from_file(self, file_path: str) -> list:
        """ Loads json data from the given file.
        """
        with open(file_path, "r") as file:
            return json.load(file)

    def load_raw_data(self, file_names: list[str]) -> list:
        """ Loads listing data from all given files.
        """

        listings = []
        for data_set in file_names:
            listings.extend(self.read_listings_from_file(data_set))

        return listings

    def prepare_data(
        self, listings: list, include_descriptions: bool = False
        ) -> tuple[str, str]:
        """ Vectorizes specified listing features and encodes the tags, for model training.
            Returns features, labels
        """

        # Prepare data for training
        if include_descriptions:
            features = [
                f"{item['title']}{item.get('description', '')}" for item in listings
            ]
        else:
            features = [f"{item['title']} " for item in listings]

        tags = [item["tags"] for item in listings]

        # Binary encoding for multi-label classification
        encoded_labels = self.mlb.fit_transform(tags)

        vectorized_features = self.vectorizer.fit_transform(features)
        return vectorized_features, encoded_labels

    def train_model(self, features, labels, testing: bool = True):
        """ Trains the model to predict tags based on the given features and labels.
        """
        
        # If we are testing, we will split the data and print a classification report to see how well the model performed.
        if testing:
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features, labels, test_size=0.2, random_state=1
            )
            # Train model
            self.model.fit(X_train, y_train)

            # Make predictions
            y_pred = self.model.predict(X_test)

            # Generate classification report
            report = classification_report(
                y_test, y_pred, target_names=self.mlb.classes_, zero_division=0
            )
            print(report)
        else:
            # Dont split data if we arent testing.
            # We want all the data points we can get
            self.model.fit(features, labels)
            self.save_model()

    def predict_listing_tags(self, listing: str) -> list[str]:
        """ Generates 1-3 of the most probable tags.
        """

        vectorized_listing = self.vectorizer.transform(listing)
        predictions = self.model.predict_proba(vectorized_listing)

        # Extract top 3 tags
        top_indices = predictions[0].argsort()[-3:][::-1]
        top_tags = self.mlb.classes_[top_indices]

        # Probabilities for the top 3
        top_probs = predictions[0][top_indices]
        
        print(f"Top tags: {top_tags}")
        print(f"Top Probs: {top_probs}")


        # If the most likely tag is fairly unprobable, assign the tag as misc
        if top_probs[0] < 0.25:
            return ["misc"]
        
        # Only return relevent tags (But always include 1)
        i = 0
        for tag_prob in top_probs:
            if tag_prob > 0.5:
                i += 1
        
        return top_tags[0:i]


def main():
    lc = ListingTagClassifier()
    
    # Enable train if you want to retrain the model
    train = True

    # If trained model doesnt exist yet, train it
    if lc.load_model() is not None or train is True:
        raw_data_files = ["raw_data.json", "more_data.json"]
        listings = lc.load_raw_data(raw_data_files)
        features, labels = lc.prepare_data(
            listings=listings, include_descriptions=False
        )

        # Train model will print a classification report if testing = True
        lc.train_model(features, labels, testing=False)

    # Predict top tags
    new_listing = ["Well used laptop backpack"]
    top_tags = lc.predict_listing_tags(new_listing)

    print(f"Top tags for the new listing: {top_tags}")


if __name__ == "__main__":
    main()
