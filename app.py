from flask import Flask, render_template, request, session, redirect, url_for
from agents.destination_agent import score_destinations
from agents.transport_agent   import get_transport_options
from agents.hotel_agent       import (get_hotels_for_destination,
                                      generate_booking_id,
                                      calculate_total_cost)
from agents.itinerary_agent import generate_itinerary
app = Flask(__name__)
app.secret_key = "smarttrip_secret_key"

# ── Home ──────────────────────────────────────────────
@app.route('/')
def home():
    return render_template('home.html')

# ── Input form ────────────────────────────────────────
@app.route('/input')
def input_page():
    return render_template('input.html')

# ── Destination recommendation ────────────────────────
@app.route('/recommend', methods=['POST'])
def recommend():
    members     = request.form.get('members')
    budget      = request.form.get('budget')
    travel_date = request.form.get('travel_date')
    days        = request.form.get('days')
    group       = request.form.get('travel_group')
    trip_type   = request.form.get('trip_type')
    city        = request.form.get('city')

    print(f"City: {city} | Group: {group} | Type: {trip_type} | Budget: {budget}")

    session['trip'] = {
        'members':     members,
        'budget':      budget,
        'travel_date': travel_date,
        'days':        days,
        'group':       group,
        'trip_type':   trip_type,
        'city':        city
    }

    recommendations = score_destinations(budget, group, trip_type, travel_date)
    return render_template('destinations.html',
                           destinations=recommendations,
                           trip=session['trip'])

# ── Destination selected → Transport page ─────────────
@app.route('/select-destination', methods=['POST'])
def select_destination():
    selected = request.form.get('destination')
    session['selected_destination'] = selected

    trip    = session.get('trip', {})
    city    = trip.get('city') or 'Chennai'
    members = trip.get('members') or 1

    options, distance, found = get_transport_options(city, selected, members)

    print(f"Route: {city} → {selected} | {distance} km | Found: {found}")

    return render_template('transport.html',
                           destination=selected,
                           options=options,
                           distance=distance,
                           found_in_data=found,
                           trip=trip)

# ── Transport selected → Hotel page ───────────────────
@app.route('/select-transport', methods=['POST'])
def select_transport():
    mode        = request.form.get('mode')
    per_person  = request.form.get('price_per_person')
    total_price = request.form.get('total_price')
    duration    = request.form.get('duration')

    session['transport'] = {
        'mode':             mode,
        'price_per_person': per_person,
        'total_price':      total_price,
        'duration':         duration
    }

    print(f"Transport: {mode} | ₹{total_price} total")
    return redirect(url_for('hotels'))

# ── Hotel page ────────────────────────────────────────
@app.route('/hotels')
def hotels():
    destination = session.get('selected_destination', '')
    trip        = session.get('trip', {})
    transport   = session.get('transport', {})

    hotel_list  = get_hotels_for_destination(destination)

    return render_template('hotels.html',
                           destination=destination,
                           hotels=hotel_list,
                           trip=trip,
                           transport=transport)

# ── Hotel selected → Confirmation ─────────────────────
@app.route('/select-hotel', methods=['POST'])
def select_hotel():
    hotel_name  = request.form.get('hotel_name')
    hotel_price = int(request.form.get('hotel_price'))
    hotel_type  = request.form.get('hotel_type')
    hotel_rating= request.form.get('hotel_rating')

    trip        = session.get('trip', {})
    transport   = session.get('transport', {})
    destination = session.get('selected_destination', '')
    days        = int(trip.get('days', 1))
    transport_total = transport.get('total_price', 0)

    # Calculate costs
    hotel_total, grand_total = calculate_total_cost(
        hotel_price, days, transport_total
    )

    # Generate booking ID
    booking_id = generate_booking_id()

    # Save to session
    session['booking'] = {
        'booking_id':    booking_id,
        'hotel_name':    hotel_name,
        'hotel_price':   hotel_price,
        'hotel_type':    hotel_type,
        'hotel_rating':  hotel_rating,
        'hotel_total':   hotel_total,
        'grand_total':   grand_total
    }

    print(f"Hotel: {hotel_name} | Booking ID: {booking_id} | Total: ₹{grand_total}")

    return redirect(url_for('confirmation'))

# ── Confirmation page ─────────────────────────────────
@app.route('/confirmation')
def confirmation():
    booking     = session.get('booking', {})
    trip        = session.get('trip', {})
    transport   = session.get('transport', {})
    destination = session.get('selected_destination', '')

    return render_template('confirmation.html',
                           booking=booking,
                           trip=trip,
                           transport=transport,
                           destination=destination)

# ── Itinerary page ────────────────────────────────────
@app.route('/itinerary')
def itinerary():
    destination = session.get('selected_destination', '')
    trip        = session.get('trip', {})
    transport   = session.get('transport', {})
    booking     = session.get('booking', {})

    days          = trip.get('days', 1)
    hotel_name    = booking.get('hotel_name', 'your hotel')
    transport_mode= transport.get('mode', 'your transport')

    # Generate the day-wise plan
    plan = generate_itinerary(destination, days, hotel_name, transport_mode)

    return render_template('itinerary.html',
                           destination=destination,
                           trip=trip,
                           transport=transport,
                           booking=booking,
                           plan=plan)

if __name__ == '__main__':
    app.run(debug=True)

