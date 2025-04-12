from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from Backend.model.User import createUser, getUser, getId, loginUser
from Backend.model.States import *
from Backend.utility.gemini import *
from Backend.model.Admin import *

session = {}
admin = Blueprint('Admin', __name__, template_folder='templates')


@admin.route('/admin/signin', methods=['GET', 'POST'])
def signin():
    if 'admin_id' in session:
        return redirect(url_for('Admin.home', id=session['admin_id']))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['passwd']  # Changed to match form field name
        if loginAdmin(username, password):
            session['admin_id'] = usernameToId(username)
            return redirect(url_for('Admin.home', id=usernameToId(username)))
        else:
            flash('Invalid username or password', 'error')
    return render_template('sign/admin/signin.html')

@admin.route('/admin/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['passwd']  
        group_name = request.form['group_name']
        if createAdmin(username, password, group_name):
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('Admin.signin'))
        else:
            flash('Username already exists', 'error')
    return render_template('sign/admin/signup.html')

@admin.route('/admin/home/<id>')
def home(id):
    if 'admin_id' in session and session['admin_id'] == id:
        try:
            # Get members list and convert to proper format
            members_ids = getMembers(id)
            members = []
            if members_ids and len(members_ids) > 0:
                for member_id in members_ids:
                    user_data = getUser(member_id)
                    if user_data:  # Only add if user data exists
                        members.append({
                            'id': user_data['_id'],
                            'name': user_data['name'],
                            'email': user_data['email']
                        })
            
            group_name = getName(id)
            return render_template('admin/home.html', 
                                 id=id, 
                                 group_name=group_name, 
                                 members=members)
        except Exception as e:
            print(f"Error in admin home: {str(e)}")
            flash('Error loading group data', 'error')
            return redirect(url_for('Admin.signin'))
    else:
        flash('You need to log in first!', 'warning')
        return redirect(url_for('Admin.signin'))

@admin.route('/admin/logout')
def logout():
    session.pop('admin_id', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('Admin.signin'))

@admin.route('/admin/user/remove/<user_id>', methods=['POST'])
def remove_user(user_id):
    if 'admin_id' in session:
        try:
            if removeUserById(user_id):
                flash('User removed successfully', 'success')
            else:
                flash('Error removing user', 'error')
        except Exception as e:
            print(f"Error removing user: {str(e)}")
            flash('Error removing user', 'error')
        return redirect(url_for('Admin.home', id=session['admin_id']))
    flash('Admin authentication required', 'error')
    return redirect(url_for('Admin.signin'))

@admin.route('/admin/user/pulse/<user_id>')
def review_pulse(user_id):
    if 'admin_id' in session:
        try:
            user = getUser(user_id)
            if not user:
                flash('User not found', 'error')
                return redirect(url_for('Admin.home', id=session['admin_id']))
            
            return render_template('admin/reviewHealth.html', 
                                 user=user,
                                 fsd=getPastFiveDaysSessionData(user_id),
                                 tsd=getTodaysSessionData(user_id),
                                 lsd=getLastSessionData(user_id))
        except Exception as e:
            print(f"Error reviewing pulse: {str(e)}")
            flash('Error loading health data', 'error')
            return redirect(url_for('Admin.home', id=session['admin_id']))
    flash('Admin authentication required', 'error')
    return redirect(url_for('Admin.signin'))
