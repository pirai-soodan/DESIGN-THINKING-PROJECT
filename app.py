from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/input')
def input_page():
    return render_template('input.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    members = request.form.get('members')
    budget = request.form.get('budget')
    travel_date = request.form.get('travel_date')
    days = request.form.get('days')
    travel_group = request.form.get('travel_group')
    trip_type    = request.form.get('trip_type')

    print("---- Trip Details Received ----")
    print(f"Members     : {members}")
    print(f"Budget      : {budget}")
    print(f"Travel Date : {travel_date}")
    print(f"Days        : {days}")
    print(f"Travel Group: {travel_group}")
    print(f"Trip Type   : {trip_type}")
    print("--------------------------------")

    return f"""
<h2>Details Received!</h2>
<p>Members: {members}</p>
<p>Budget: ₹{budget}</p>
<p>Travel Date: {travel_date}</p>
<p>Days: {days}</p>
<p>Travel Group: {travel_group}</p>
<p>Trip Type: {trip_type}</p>
<a href="/input">Go Back</a>
"""

if __name__ == '__main__':
    app.run(debug=True)