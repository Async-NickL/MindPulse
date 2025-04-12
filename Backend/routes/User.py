from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from Backend.model.User import *
from Backend.model.States import *
from Backend.utility.gemini import *
from Backend.model.Admin import *
from Backend.utility.map import *
from datetime import datetime
from dotenv import load_dotenv
import os

user = Blueprint('User', __name__, template_folder='templates')

load_dotenv()

@user.route('/')
def index():
    return render_template('sign/Hero.html')

@user.route('/sign/<type>')
def sign(type):
    return render_template('sign/sign.html', type=type)

@user.route('/user/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['passwd']
            
            # First check if user exists by email
            user_id = getId(email)
            if user_id is None:  # Changed from if not user_id
                flash('No account found with this email', 'error')
                print(f'No account found with email: {email}')
                return render_template('sign/user/signin.html')
            
            # Then verify password
            if loginUser(email, password):
                session['user_id'] = user_id
                session['email'] = email
                session['is_authenticated'] = True
                print(f'User logged in successfully: {email}')
                return redirect(url_for('User.home', id=user_id))
            else:
                flash('Invalid password', 'error')
                print(f'Invalid password for email: {email}')
                return render_template('sign/user/signin.html')
                
        except Exception as e:
            print(f"Login error: {str(e)}")
            flash('An error occurred during login', 'error')
            return render_template('sign/user/signin.html')
            
    return render_template('sign/user/signin.html')

@user.route('/user/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['uname']
        email = request.form['email']
        profession = request.form['profession']
        age = request.form['age']
        gender = request.form['gender']
        password = request.form['passwd']
        if getId(email):
            flash('An account with this email already exists', 'error')
            return render_template("sign/user/signup.html")
            
        if createUser(username, email, profession, age, gender, password, []):
            user_id = getId(email)
            session['user_id'] = user_id
            session['email'] = email
            session['is_authenticated'] = True
            return redirect(url_for('User.home', id=user_id))
        else:
            flash('Error creating account', 'error')
            
    return render_template("sign/user/signup.html")

@user.route('/home/<id>')
def home(id):
    if 'user_id' in session and session['user_id'] == id:
        user = getUser(id)
        last_session_data = getLastSessionData(id)
        
        # Only calculate and show score if there's actual session data
        if last_session_data:
            try:
                avg = (last_session_data['stress'] + last_session_data['anxiety'] + last_session_data['anger']) / 3
                last_session_data['avg'] = round(avg)
            except (KeyError, TypeError):
                last_session_data = None
        
        return render_template('pages/home.html', id=id, user=user, lsd=last_session_data)
    else:
        flash('You need to log in first!', 'warning')
        return redirect(url_for('User.signin'))



@user.route('/dashboard/<id>')
def dashboard(id):
    if 'user_id' in session and session['user_id'] == id:
        user = getUser(id)
        five_day_data = getPastFiveDaysSessionData(id)
        today_data = getTodaysSessionData(id)
        last_session_data = getLastSessionData(id)
        print("five_day_data: ", five_day_data)
        print("today_data: ", today_data)
        print("last_session_data: ", last_session_data)
        return render_template('pages/dashboard.html', id=id, user=user, fsd=five_day_data, tsd=today_data, lsd=last_session_data)
    else:
        flash('You need to log in first!', 'warning')
        return redirect(url_for('User.signin'))


@user.route('/session/<id>')
def session_route(id):
    if 'user_id' in session and session['user_id'] == id:
        user = getUser(id)
        if user:
            profession = user['profession']
            gender = user['gender']
            age = user['age']
            anxiety = getQuestions(profession=profession,age=age,gender=gender,emotion_type="anxiety")
            anger = getQuestions(profession=profession,age=age,gender=gender,emotion_type="anger")
            stress = getQuestions(profession=profession,age=age,gender=gender,emotion_type="stress")
            return render_template('pages/session.html',id=id,anxiety=anxiety,anger=anger,stress=stress)
        return redirect(url_for('User.dashboard', id=id))
    else:
        flash('You need to log in first!', 'warning')
        return redirect(url_for('User.signin'))
    

@user.route('/calculate/<id>', methods=['POST'])
def calculate(id):
    if 'user_id' in session and session['user_id'] == id:
        if request.method == 'POST':
            try:
                # Initialize scores
                stress_score = anxiety_score = anger_score = 0
                error_messages = []

                # Process stress answers
                stress_answers = {}
                for i in range(2):
                    q_key = f'stress_{i}'
                    stress_answers[request.form.get(f'stress_q{i+1}')] = request.form.get(q_key)
                stress_score = calculateScore('stress', stress_answers)
                if stress_score == False or stress_score > 100:
                    error_messages.append("Your stress answers seem unrelated to the questions. Please answer more specifically.")

                # Process anxiety answers
                anxiety_answers = {}
                for i in range(2):
                    q_key = f'anxiety_{i}'
                    anxiety_answers[request.form.get(f'anxiety_q{i+1}')] = request.form.get(q_key)
                anxiety_score = calculateScore('anxiety', anxiety_answers)
                if anxiety_score == False or anxiety_score > 100:
                    error_messages.append("Your anxiety answers seem unrelated to the questions. Please answer more specifically.")

                # Process anger answers
                anger_answers = {}
                for i in range(2):
                    q_key = f'anger_{i}'
                    anger_answers[request.form.get(f'anger_q{i+1}')] = request.form.get(q_key)
                anger_score = calculateScore('anger', anger_answers)
                if anger_score == False or anger_score > 100:
                    error_messages.append("Your anger answers seem unrelated to the questions. Please answer more specifically.")

                # Check for any errors
                if error_messages:
                    for message in error_messages:
                        flash(message, 'error')
                    return redirect(url_for('User.session_route', id=id))

                # Validate all scores are within range
                if not all(isinstance(score, (int, float)) and 0 <= score <= 100 
                          for score in [stress_score, anxiety_score, anger_score]):
                    flash('Please provide relevant answers to all questions', 'error')
                    return redirect(url_for('User.session_route', id=id))

                # Save to database
                current_date = datetime.now().strftime("%d-%m-%Y")
                if appendSessionData(id, stress_score, anxiety_score, anger_score):
                    flash('Session recorded successfully!', 'success')
                    return redirect(url_for('User.dashboard', id=id))
                else:
                    flash('Error saving session data', 'error')
                    return redirect(url_for('User.session_route', id=id))

            except Exception as e:
                print(f"Error in calculate route: {str(e)}")
                flash('Error processing your responses. Please try again.', 'error')
                return redirect(url_for('User.session_route', id=id))
    
    flash('Please login first', 'warning')
    return redirect(url_for('User.signin'))

@user.route('/communities/<id>')
def communities(id):
    if 'user_id' in session and session['user_id'] == id:
        user_groups = getUsersGroups(id)
        if user_groups:
            # Convert group IDs to group names
            group_info = []
            for group_id in user_groups:
                group_name = getName(group_id)
                if group_name:
                    group_info.append({
                        'id': group_id,
                        'name': group_name
                    })
            return render_template('pages/communities.html', id=id, user_groups=group_info)
        return render_template('pages/communities.html', id=id)
    else:
        flash('You need to log in first!', 'warning')
        return redirect(url_for('User.signin'))

@user.route('/logout/<id>')
def logout(id):
    if 'user_id' in session and session['user_id'] == id:
        session.clear()
        flash('Successfully logged out', 'success')
    return redirect(url_for('User.index'))


@user.route('/join-group/<id>', methods=['POST'])
def join_group(id):
    if 'user_id' in session and session['user_id'] == id:
        group_code = request.form['group_code']
        if joinGroup(id, group_code):
            group_name = getName(group_code)
            return redirect(url_for('User.communities', id=id))
        else:
            flash('Error joining group', 'error')
            return redirect(url_for('User.communities', id=id))
    else:
        flash('You need to log in first!', 'warning')
        return redirect(url_for('User.signin'))

@user.route('/nearby')
def nearby():
    return render_template('pages/nearby.html', 
                         opencage_api_key=os.getenv('OPENCAGE_API_KEY'))

@user.route('/get-nearby-places/<id>', methods=['POST'])
def get_nearby_places(id):
    if 'user_id' in session and session['user_id'] == id:
        try:
            data = request.get_json()
            lat = float(data['lat'])
            lon = float(data['lon'])
            places = get_nearby_medical_places(lat, lon)
            return jsonify({'places': places})
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    return jsonify({'error': 'Unauthorized'}), 401

