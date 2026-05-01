from functools import wraps
from flask import Flask, render_template, request, session, redirect, url_for, flash
from agents.destination_agent  import score_destinations
from agents.itinerary_agent    import generate_itinerary
from agents.ai_agent           import (get_ai_destination_reason,
                                       get_ai_itinerary,
                                       get_ai_travel_tip,
                                       get_ai_flight_recommendation,
                                       get_ai_train_recommendation,
                                       get_ai_hotel_review)
from agents.auto_booking_agent import (generate_train_options,
                                       generate_flight_options,
                                       book_selected_ticket,
                                       auto_book_hotel,
                                       generate_transaction_id,
                                       get_distance)
from database.auth import (init_bcrypt, signup_user,
                            login_user, save_trip_to_db, get_user_trips)
from agents.weather_agent import get_real_weather
from datetime import datetime

app = Flask(__name__)
app.secret_key = "smarttrip_secret_key_2025"

# Init bcrypt
init_bcrypt(app)

# ── Login required decorator ──────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            session['next'] = request.url
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ─────────────────────────────────────────────────────
# AUTH ROUTES
# ─────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('home'))
    error = None
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        success, result = login_user(email, password)
        if success:
            session['user'] = result
            print(f"Login: {email}")
            next_url = session.pop('next', url_for('home'))
            return redirect(next_url)
        else:
            error = result
    return render_template('login.html', error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user' in session:
        return redirect(url_for('home'))
    error = None
    success_msg = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm  = request.form.get('confirm_password', '').strip()
        if password != confirm:
            error = "Passwords do not match"
        else:
            ok, msg = signup_user(username, email, password)
            if ok:
                success_msg = "Account created! Please log in."
            else:
                error = msg
    return render_template('signup.html', error=error, success=success_msg)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    user  = session.get('user', {})
    trips = get_user_trips(user.get('email', ''))
    return render_template('profile.html', user=user, trips=trips)

# ─────────────────────────────────────────────────────
# MAIN ROUTES
# ─────────────────────────────────────────────────────

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/input')
@login_required
def input_page():
    return render_template('input.html')

@app.route('/recommend', methods=['POST'])
@login_required
def recommend():
    members     = request.form.get('members')
    budget      = request.form.get('budget')
    travel_date = request.form.get('travel_date')
    days        = request.form.get('days')
    group       = request.form.get('travel_group')
    trip_type   = request.form.get('trip_type')
    city        = request.form.get('city')

    print(f"City:{city} | Group:{group} | Type:{trip_type} | Budget:{budget}")

    session['trip'] = {
        'members': members, 'budget': budget,
        'travel_date': travel_date, 'days': days,
        'group': group, 'trip_type': trip_type, 'city': city
    }

    recommendations = score_destinations(budget, group, trip_type, travel_date)

    # Gemini AI adds reason for each destination
    for dest in recommendations:
        dest['ai_reason'] = get_ai_destination_reason(
            dest['name'], trip_type, group, budget
        )

    return render_template('destinations.html',
                           destinations=recommendations,
                           trip=session['trip'])

@app.route('/select-destination', methods=['POST'])
@login_required
def select_destination():
    selected = request.form.get('destination')
    session['selected_destination'] = selected
    trip    = session.get('trip', {})
    city    = trip.get('city') or 'Chennai'
    members = trip.get('members') or 1
    budget  = int(trip.get('budget', 10000))
    budget_per_person = budget // int(members)
    distance = get_distance(city, selected)

    # Generate ticket options for both train and flight
    trains  = generate_train_options(city, selected, distance, budget_per_person, members)
    flights = generate_flight_options(city, selected, distance, budget_per_person, members)

    # Gemini AI recommendations
    train_ai = get_ai_train_recommendation(city, selected, members)
    flight_ai = get_ai_flight_recommendation(city, selected, budget_per_person, members) if flights else None

    session['ticket_options'] = {
        'trains':  trains,
        'flights': flights,
        'distance': distance
    }

    return render_template('choose_ticket.html',
                           trains=trains,
                           flights=flights,
                           train_ai=train_ai,
                           flight_ai=flight_ai,
                           destination=selected,
                           distance=distance,
                           trip=trip)

@app.route('/select-ticket', methods=['POST'])
@login_required
def select_ticket():
    import json
    ticket_json = request.form.get('ticket_data')
    ticket = json.loads(ticket_json)

    # Generate booking confirmation
    booking_details = book_selected_ticket(ticket)

    session['selected_ticket'] = ticket
    session['ticket_booking']  = booking_details
    session['transport'] = {
        'mode':             ticket['type'].capitalize(),
        'price_per_person': ticket['price_per_person'],
        'total_price':      ticket['total_price'],
        'duration':         ticket['duration']
    }

    return redirect(url_for('booking_process'))

@app.route('/booking-process')
@login_required
def booking_process():
    ticket  = session.get('selected_ticket', {})
    booking = session.get('ticket_booking', {})
    trip    = session.get('trip', {})
    dest    = session.get('selected_destination', '')

    # Auto-select hotel
    budget_pp = int(trip.get('budget', 10000)) // max(int(trip.get('members', 1)), 1)
    hotel = auto_book_hotel(dest, budget_pp, trip.get('days', 1))
    session['hotel'] = hotel

    ticket_cost = ticket.get('total_price', 0)
    hotel_cost  = hotel['hotel_total']
    grand_total = ticket_cost + hotel_cost
    session['grand_total'] = grand_total

    return render_template('booking_process.html',
                           ticket=ticket,
                           booking=booking,
                           hotel=hotel,
                           grand_total=grand_total,
                           trip=trip,
                           destination=dest)

@app.route('/payment')
@login_required
def payment():
    return render_template(
    'payment.html',
    ticket=session.get('selected_ticket', {}),
    hotel=session.get('hotel', {}),
    booking=session.get('ticket_booking', {}),  # ✅ ADD THIS
    grand_total=session.get('grand_total', 0),
    trip=session.get('trip', {}),
    destination=session.get('selected_destination', '')
)

@app.route('/process-payment', methods=['POST'])
@login_required
def process_payment():
    pay_method = request.form.get('pay_method', 'upi')
    pay_name   = request.form.get('pay_detail', '')
    txn_id     = generate_transaction_id()

    session['transaction'] = {
        'id': txn_id, 'method': pay_method,
        'name': pay_name, 'status': 'SUCCESS'
    }

    # Save trip to MongoDB
    trip    = session.get('trip', {})
    ticket  = session.get('selected_ticket', {})
    hotel   = session.get('hotel', {})
    booking = session.get('ticket_booking', {})
    user    = session.get('user', {})

    save_trip_to_db(user.get('email', ''), {
        'destination':   session.get('selected_destination', ''),
        'travel_date':   trip.get('travel_date', ''),
        'days':          trip.get('days', 1),
        'members':       trip.get('members', 1),
        'transport_mode':ticket.get('type', ''),
        'hotel_name':    hotel.get('name', ''),
        'grand_total':   session.get('grand_total', 0),
        'booking_id':    booking.get('pnr', '')
    })

    print(f"Payment: {txn_id} | {pay_method}")
    return redirect(url_for('ticket_confirmed'))

@app.route('/ticket')
@login_required
def ticket_confirmed():
    return render_template('ticket.html',
                           ticket=session.get('selected_ticket', {}),
                           booking=session.get('ticket_booking', {}),
                           hotel=session.get('hotel', {}),
                           grand_total=session.get('grand_total', 0),
                           transaction=session.get('transaction', {}),
                           trip=session.get('trip', {}),
                           destination=session.get('selected_destination', ''))

@app.route('/itinerary')
@login_required
def itinerary():
    trip        = session.get('trip', {})
    hotel       = session.get('hotel', {})
    transport   = session.get('transport', {})
    destination = session.get('selected_destination', '')
    days        = trip.get('days', 1)
    hotel_name  = hotel.get('name', 'your hotel')
    t_mode      = transport.get('mode', 'your transport')
    trip_type   = trip.get('trip_type', 'fun')
    travel_date = trip.get('travel_date', '')

    month = ''
    if travel_date:
        try:
            month = datetime.strptime(travel_date, "%Y-%m-%d").strftime("%B")
        except:
            pass

    weather    = get_real_weather(destination)
    ai_plan    = get_ai_itinerary(destination, days, hotel_name, t_mode, trip_type)
    travel_tip = get_ai_travel_tip(destination, month)
    rule_plan  = generate_itinerary(destination, days, hotel_name, t_mode)

    return render_template('itinerary.html',
                           destination=destination,
                           trip=trip,
                           transport=transport,
                           hotel=hotel,
                           plan=rule_plan,
                           ai_plan_text=ai_plan,
                           weather=weather,
                           travel_tip=travel_tip)

@app.route('/confirmation')
@login_required
def confirmation():
    return render_template('ticket.html',
                           ticket=session.get('selected_ticket', {}),
                           booking=session.get('ticket_booking', {}),
                           hotel=session.get('hotel', {}),
                           grand_total=session.get('grand_total', 0),
                           transaction=session.get('transaction', {}),
                           trip=session.get('trip', {}),
                           destination=session.get('selected_destination', ''))
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)