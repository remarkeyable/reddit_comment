import os
from flask import Flask, jsonify, request
import praw

# Set up Reddit API using environment variables
reddit = praw.Reddit(
    client_id=os.environ.get('REDDIT_CLIENT_ID'),
    client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
    user_agent='CommentExtractor by /u/{}'.format(os.environ.get('REDDIT_USERNAME', 'anonymous'))
)

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the Reddit Comment Extractor API",
        "usage": {
            "endpoint": "/comments",
            "method": "GET",
            "description": "Extracts all top-level and nested comments from a Reddit post.",
            "query_parameters": {
                "url": "The full URL of the Reddit post (e.g., https://www.reddit.com/r/AskReddit/comments/abcd1234/example_post/)"
            },
            "example": "/comments?url=https://www.reddit.com/r/AskReddit/comments/abcd1234/example_post/"
        },
    })

@app.route('/comments', methods=['GET'])
def get_comments():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing Reddit post URL'}), 400

    try:
        submission = reddit.submission(url=url)
        submission.comments.replace_more(limit=0)

        comments = [
            {
                'author': comment.author.name if comment.author else '[deleted]',
                'body': comment.body,
                'score': comment.score
            }
            for comment in submission.comments.list()
        ]

        return jsonify({
            'title': submission.title,
            'url': url,
            'num_comments': len(comments),
            'comments': comments
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
