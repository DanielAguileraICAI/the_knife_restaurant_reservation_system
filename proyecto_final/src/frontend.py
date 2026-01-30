
from flask import Blueprint, render_template

frontend_bp = Blueprint(
	"frontend",
	__name__,
	template_folder="templates",
	static_folder="static",
	static_url_path="/static",
)


@frontend_bp.route("/")
def index():
	return render_template("index.html")


@frontend_bp.route("/restaurants")
def restaurants():
	return render_template("restaurants.html")


@frontend_bp.route("/reservations")
def reservations():
	return render_template("reservations.html")


@frontend_bp.route("/clients")
def clients():
	return render_template("clients.html")


@frontend_bp.route("/book")
def book():
	return render_template("book.html")


@frontend_bp.route("/restaurant-area")
def restaurant_area():
	return render_template("restaurant_area.html")

