from flask import Flask, render_template
from batch_job import analyze_service_metrics

app = Flask(__name__)

# MySQL connection details
mysql_url = "jdbc:mysql://172.25.160.1:3306/LogRecords"
mysql_user = "root"
mysql_password = "thanishkn11"

@app.route('/')
def metrics():
    data = analyze_service_metrics(mysql_url, mysql_user, mysql_password)
    return render_template("index.html", metrics=data)

if __name__ == '__main__':
    app.run(debug=True)
