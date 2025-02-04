from flask import Flask, render_template, request, send_from_directory
from src.map import get_static_bus_route
from src.df_processing import get_recent_timestamp, get_bus_number_alert
import os

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    """Main page where users can input a bus number and view the map."""
    if request.method == "POST":
        bus_number = request.form.get("bus_number") 
        map_file = get_static_bus_route(bus_number)
        bus_alert = get_bus_number_alert(bus_number)
        update_timestamp = get_recent_timestamp()

        if not map_file:
            return render_template(
                "index.html", error="Invalid Bus Number or No Data Found"
            )

        return render_template(
            "index.html",
            map_file="toronto_map.html",
            update_timestamp=update_timestamp,
            bus_alert=bus_alert,
        )

    return render_template("index.html")


@app.route("/toronto_map.html")
def serve_map():
    """Serve the generated map file from the templates directory."""
    return send_from_directory(
        os.path.join(os.getcwd(), "templates"), "toronto_map.html"
    )


if __name__ == "__main__":
    app.run(debug=True)
