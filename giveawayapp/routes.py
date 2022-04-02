import io, random, time
from giveawayapp import app, db
from giveawayapp.models import User, Lists, Giveaway, Winners
from werkzeug.urls import url_parse
from giveawayapp.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, url_for, request, session, redirect, flash
from werkzeug.utils import secure_filename
import os

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):     
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        user.save()
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
@app.route('/home')
@login_required
def home():
    cr_user = current_user.username
    return render_template('index.html', cr_user=cr_user)


@app.route('/run', methods=['GET', 'POST'])
@login_required
def run():
    message = ""
    giveaway = Giveaway.objects(username=current_user.username)
    list = Lists.objects(username=current_user.username)
    if request.method == 'POST':
        # check if the post request has the file part
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            UPLOAD_FOLDER = './giveawayapp/public/'
            file.save(os.path.join(UPLOAD_FOLDER, filename))

        giveaway = Giveaway(giveaway=request.form.get('giveaway'), username = current_user.username, lists=request.form.get('lists'), filename = filename, quantity=request.form.get('quantity'))
        giveaway.save()
        message = "Form Submitted Succussfully"
        
    return render_template('run.html', lists=list, message=message, giveaway=giveaway)

@app.route('/list', methods=['GET', 'POST'])
@login_required
def list():
    list = Lists.objects(username=current_user.username)
    if request.method == 'POST':
        list = Lists(listname=request.form.get('listname'), username = current_user.username, lists=request.form.get('lists'))
        # print(request.form.get('lists'))
        list.save()

    return render_template('list.html', lists=list)




@app.route('/play/<string:id>', methods=['GET', 'POST'])
@login_required
def play(id):
    identifier = Giveaway.objects(id=id).first()
    name = identifier.giveaway
    filename = identifier.filename
    listname = identifier.lists
    username = identifier.username
    quantity = identifier.quantity
    items = [""]
    winner = [""]
    wins = [""]

    userlist = Lists.objects(listname=listname).first()
    lists = userlist.lists
    # print(lists)
    if Winners.objects(iden=id).first():
        winlist = Winners.objects(iden=id).first()
        wins = winlist.winners  
        # print(wins)  
        return render_template('winners.html', wins=wins, filename=filename, giveaway = name)
    else:
        if request.method == 'POST':
            time.sleep(2)
            
            buf = io.StringIO(lists)
            items = lists.split("\r\n")
            lines = buf.readline()
            allwinlist = Winners.objects(listname=listname)
            if allwinlist:      
                for winnerslist in allwinlist:
                    allwins = winnerslist.winners
                    print(allwins)
                # print(items)
                    for awon in allwins:  
                        if awon in items:  
                            items.remove(awon)
                            winner = random.sample(items, quantity)
            else:
                winner = random.sample(items, quantity)
                    
                    
            winadd = Winners( giveaway = name, listname=listname, winners=winner, username=username, lists=lists, iden=id)
            winadd.save()

            # print("button pushed", lines, winner)
            return render_template('winners.html', wins=winner, filename=filename, giveaway=name)


    return render_template('play.html', name = name, filename=filename, listname =listname, lists= lists, id=id, quantity=quantity, items=wins)