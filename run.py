from giveawayapp import app, db
from giveawayapp.models import User, Lists, Giveaway, Winners


if __name__ == "__main__":
    app.run(port=5000, debug=False)
