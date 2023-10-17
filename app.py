from flask import Flask, render_template, request
from imdb import IMDb
from textblob import TextBlob

app = Flask(__name__)

def get_movie_info(movie_title):
    ia = IMDb()
    movies = ia.search_movie(movie_title)
    
    if not movies:
        return [], "Movie not found", "N/A", "N/A", 0, 0, 0
    
    movie = movies[0]
    ia.update(movie, ["reviews"])
    
    reviews = [{"content": review["content"], "sentiment": analyze_sentiment(review["content"])} for review in movie["reviews"]]
    rating = movie.data.get("rating", "N/A")
    overall_sentiment = analyze_overall_sentiment(reviews)

    positive_count, neutral_count, negative_count = count_sentiments(reviews)

    return reviews, rating, overall_sentiment, positive_count, neutral_count, negative_count

def analyze_sentiment(review):
    polarity_score = TextBlob(review).sentiment.polarity
    
    if polarity_score > 0.1:
        return "Positive"
    elif polarity_score < -0.1:
        return "Negative"
    else:
        return "Neutral"

def analyze_overall_sentiment(reviews):
    polarity_scores = [TextBlob(review["content"]).sentiment.polarity for review in reviews]
    average_sentiment = sum(polarity_scores) / len(polarity_scores)
    
    if average_sentiment > 0.1:
        return "Positive"
    elif average_sentiment < -0.1:
        return "Negative"
    else:
        return "Neutral"

def count_sentiments(reviews):
    positive_count = sum(1 for review in reviews if review["sentiment"] == "Positive")
    neutral_count = sum(1 for review in reviews if review["sentiment"] == "Neutral")
    negative_count = sum(1 for review in reviews if review["sentiment"] == "Negative")

    return positive_count, neutral_count, negative_count

@app.route("/", methods=["GET", "POST"])
def index():
    movie_name = ""
    positive_count = 0
    neutral_count = 0
    negative_count = 0

    if request.method == "POST":
        movie_title = request.form["movie_title"]
        reviews, rating, overall_sentiment, positive_count, neutral_count, negative_count = get_movie_info(movie_title)
        movie_name = movie_title  # Set the movie name for display
        return render_template("index.html", reviews=reviews, rating=rating, overall_sentiment=overall_sentiment,
                               positive_count=positive_count, neutral_count=neutral_count, negative_count=negative_count,
                               movie_name=movie_name)
    
    return render_template("index.html", positive_count=positive_count, neutral_count=neutral_count, negative_count=negative_count, movie_name=movie_name)

if __name__ == "__main__":
    app.run(debug=True)
