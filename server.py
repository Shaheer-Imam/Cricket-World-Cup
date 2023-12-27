from flask import Flask, jsonify, render_template
from Service.points_table import PointsTable

app = Flask(__name__)

@app.route('/')
def home():
    df = PointsTable.get_team_points_table()
    table_html = df.to_html(classes="table table-bordered table-stripped")
    return render_template("index.html", table_html=table_html)

if __name__ == "__main__":
    app.run(debug=True)