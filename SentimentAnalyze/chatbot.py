#install the sklearn library for this program to work
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

# Sample data
data = {
    'text': [
        "I love this product!",
        "This is the worst experience I've ever had.",
        "I am feeling great today.",
        "This is okay, not the best but not the worst.",
        "I absolutely hate this!",
        "What a fantastic service!",
        "I do not like this at all."
    ],
    'sentiment': [
        "positive",
        "negative",
        "positive",
        "neutral",
        "negative",
        "positve",
        "negative"
    ]
}

# Create a DataFrame for the data to be trained
df = pd.DataFrame(data)

# Function to train the model
def train_model(df):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(df['text'])
    y = df['sentiment']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LogisticRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred, zero_division=0))
    return vectorizer, model

# Training the initial model
vectorizer, model = train_model(df)

# Function to analyze sentiment
def analyze_sentiment(user_input):
    user_input_vectorized = vectorizer.transform([user_input])
    prediction = model.predict(user_input_vectorized)[0]
    return prediction

# Function for chatbot response
def chatbot_response(user_input):
    sentiment = analyze_sentiment(user_input)
    feedback = {
        'positive': "I'm glad to hear that! 😊",
        'negative': "I'm sorry to hear that. How can I assist you? 😟",
        'neutral': "Thank you for sharing your thoughts! 🤔"
    }
    response = feedback.get(sentiment, "Thank you for your feedback!")
    return response, sentiment

# Function to update the model with user feedback
def update_model(user_input, correct_sentiment):
    global df, vectorizer, model
    # Update the dataset with the correct sentiment
    new_data = pd.DataFrame({'text': [user_input], 'sentiment': [correct_sentiment]})
    df = pd.concat([df, new_data], ignore_index=True)
    # Retraining the model with updated dataset
    vectorizer, model = train_model(df)
    print("Model updated with new feedback.")

# Main loop
while True:
    print("type [exit] to stop the loop")
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    response, sentiment = chatbot_response(user_input)
    print(f"Chatbot: {response}")

    # Collect user feedback
    user_feedback = input("Was the sentiment classification correct? (yes/no): ").strip().lower()
    if user_feedback == 'no':
        correct_sentiment = input("Please provide the correct sentiment (positive/negative/neutral): ").strip().lower()
        if correct_sentiment in ['positive', 'negative', 'neutral']:
            update_model(user_input, correct_sentiment)
        else:
            print("Invalid sentiment provided.")
    else:
        print("Thank you for your feedback!")
