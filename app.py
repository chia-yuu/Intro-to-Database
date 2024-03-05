from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from sqlalchemy import func, literal_column, union_all
from sqlalchemy import and_, or_
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:12345678@final-project.cye9lhoibgi9.us-east-1.rds.amazonaws.com/animals"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '12345'
db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User class for Flask-Login
class User(UserMixin, db.Model):
    __tablename__ = 'account'
    account_name = db.Column(db.String(60))
    email = db.Column(db.String(30), primary_key=True)
    password = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    gender = db.Column(db.String(3))
    city_id = db.Column(db.Integer)
    def get_id(self):
        return str(self.email)
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class speciesTable(db.Model):
    __tablename__ = 'species'
    species_id = db.Column(db.Integer, primary_key=True)
    species_name = db.Column(db.String(30))
    
class breedTable(db.Model):
    __tablename__ = 'breed'
    breed_id = db.Column(db.Integer, primary_key=True)
    breed_name = db.Column(db.String(30))
    species_id = db.Column(db.Integer)
    
class colorTable(db.Model):
    __tablename__ = 'color'
    color_id = db.Column(db.Integer, primary_key=True)
    color_name = db.Column(db.String(20))
    
class cityTable(db.Model):
    __tablename__ = 'city'
    city_id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(10))
    
class regionTable(db.Model):
    __tablename__ = 'region'
    region_id = db.Column(db.Integer, primary_key=True)
    region_name = db.Column(db.String(20))
    city_id = db.Column(db.Integer)
    
class stray_ani(db.Model):
    __tablename__ = 'stray_ani'
    stray_id = db.Column(db.Integer, primary_key=True)
    color_id = db.Column(db.Integer)
    region_id = db.Column(db.Integer)
    city_id = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    stray_gender = db.Column(db.String(3))
    solved = db.Column(db.String(3))
    species_id = db.Column(db.Integer)
    breed_id = db.Column(db.Integer)
    user_email = db.Column(db.String(50))

class found_ani(db.Model):
    __tablename__ = 'found_ani'
    found_id = db.Column(db.Integer, primary_key = True)
    color_id = db.Column(db.Integer)
    region_id = db.Column(db.Integer)
    city_id = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    found_gender = db.Column(db.String(3))
    solved = db.Column(db.String(3))
    species_id = db.Column(db.Integer)
    breed_id = db.Column(db.Integer)
    shelter_id = db.Column(db.Integer)
    user_email = db.Column(db.String(50))
    
class shelter(db.Model):
    __tablename__ = 'shelter'
    shelter_id = db.Column(db.Integer, primary_key=True)
    shelter_name = db.Column(db.String(30))
    address = db.Column(db.String(100))
    
class shelter_phone(db.Model):
    __tablename__ = 'shelter_phone'
    id = db.Column(db.Integer, primary_key=True)
    shelter_id = db.Column(db.Integer, db.ForeignKey('shelter.shelter_id'))
    phone = db.Column(db.String(30))
    
@app.route('/', methods=['GET', 'POST'])
def index():
    title = '浪浪之家'

    if request.method == 'POST':
        selected_option = request.form.get('select_option')
        if selected_option == 'option1':
            if current_user.is_authenticated:
                return redirect(url_for('page2'))
            else:
                return redirect(url_for('login'))
        elif selected_option == 'option2':
            return redirect(url_for('page3'))
        elif selected_option == 'option3':
            return redirect(url_for('login'))
        elif selected_option == 'option4':
            return redirect(url_for('shelter_info'))
    print(f"current_user.is_authenticated: {current_user.is_authenticated}")
    print(f"current_user: {current_user}")
        
    if current_user.is_authenticated:
        greeting = f"Hello, {current_user.account_name}! <a href='{url_for('dashboard')}'>點此進入使用者介面</a>"
        greeting2 = f"<a href='{ url_for('logout') }'>點此登出</a>"
    else:
        greeting = "Welcome to 浪浪之家!"
        greeting2=""
        

    return render_template('page1.html', title=title, greeting=greeting, greeting2=greeting2)

@app.route('/page2')
def page2():
    title = '我要申報'
    species_names = speciesTable.query.all()
    breed_names = breedTable.query.all()
    color_names = colorTable.query.all()
    city_names = cityTable.query.all()
    region_names = regionTable.query.all()
    return render_template('page2.html', title=title, breed_names=breed_names, species_names=species_names, color_names=color_names ,city_names=city_names, region_names=region_names)

@app.route('/page3', methods=['GET', 'POST'])
def page3():
    title = '我要幫忙'
    if request.method == 'POST':
        selected_option = request.form.get('selection')
        if selected_option=="back":
            return redirect(url_for('index'))
    species_names = speciesTable.query.all()
    breed_names = breedTable.query.all()
    color_names = colorTable.query.all()
    city_names = cityTable.query.all()
    region_names = regionTable.query.all()
    if request.method == 'POST':
        select_species = request.form.get('whatspecies')
        select_breed = request.form.get('whatbreed')
        select_color = request.form.get('whatcolor')
        select_gender = request.form.get('whatgender')
        select_city = request.form.get('whatcity')
        select_area = request.form.get('whatarea')
        select_date = request.form.get('whatdate')
        
        # If the selected value is "未知", set it to None for filtering
        if select_species == "0":
            select_species = None
        if select_breed == "0":
            select_breed = None
        if select_color == "0":
            select_color = None
        if select_gender == "0":
            select_gender = None
        if select_city == "0":
            select_city = None
        if select_area == "0":
            select_area = None

        found_animals = (
    db.session.query(
        found_ani.user_email,
        found_ani.found_id,
        speciesTable.species_name,
        breedTable.breed_name,
        colorTable.color_name,
        found_ani.found_gender,
        cityTable.city_name,
        regionTable.region_name,
        found_ani.date,
        found_ani.solved
    )
    .join(speciesTable, found_ani.species_id == speciesTable.species_id)
    .join(breedTable, found_ani.breed_id == breedTable.breed_id)
    .join(colorTable, found_ani.color_id == colorTable.color_id)
    .join(cityTable, found_ani.city_id == cityTable.city_id)
    .join(regionTable, found_ani.region_id == regionTable.region_id)
    .filter(
        and_(
            (found_ani.species_id == select_species if select_species is not None else True),
            (found_ani.breed_id == select_breed if select_breed is not None else True),
            (found_ani.color_id == select_color if select_color is not None else True),
            (found_ani.found_gender == select_gender if select_gender is not None else True),
            (found_ani.city_id == select_city if select_city is not None else True),
            (found_ani.region_id == select_area if select_area is not None else True),
            (found_ani.date >= select_date if (select_date is not None and select_date != "") else True)
        )
    )
    .order_by(found_ani.found_id) 
    .all()
)
        stray_animals = (
    db.session.query(
        stray_ani.user_email,
        stray_ani.stray_id,
        speciesTable.species_name,
        breedTable.breed_name,
        colorTable.color_name,
        stray_ani.stray_gender,
        cityTable.city_name,
        regionTable.region_name,
        stray_ani.date,
        stray_ani.solved
    )
    .join(speciesTable, stray_ani.species_id == speciesTable.species_id)
    .join(breedTable, stray_ani.breed_id == breedTable.breed_id)
    .join(colorTable, stray_ani.color_id == colorTable.color_id)
    .join(cityTable, stray_ani.city_id == cityTable.city_id)
    .join(regionTable, stray_ani.region_id == regionTable.region_id)
    # Add your filtering logic here based on user input
    .filter(
        # Replace the following lines with your existing filtering logic
        (stray_ani.species_id == select_species if select_species is not None else True),
        (stray_ani.breed_id == select_breed if select_breed is not None else True),
        (stray_ani.color_id == select_color if select_color is not None else True),
        (stray_ani.stray_gender == select_gender if select_gender is not None else True),
        (stray_ani.city_id == select_city if select_city is not None else True),
        (stray_ani.region_id == select_area if select_area is not None else True),
        (stray_ani.date >= select_date if (select_date is not None and select_date != "") else True)
        # Add more conditions as needed based on your requirements
    )
    .order_by(stray_ani.stray_id) 
    .all()
)
        
        return render_template('page3.html', title=title, breed_names=breed_names, species_names=species_names, color_names=color_names,city_names=city_names, region_names=region_names, found_animals=found_animals, stray_animals=stray_animals)
    return render_template('page3.html', title=title, breed_names=breed_names, species_names=species_names, color_names=color_names,city_names=city_names, region_names=region_names)

@app.route('/shelter_info', methods=['GET'])
def shelter_info():
    shelter_data = (
        db.session.query(
            shelter.shelter_name,
            shelter.address,
            shelter_phone.phone
        )
        .join(shelter_phone, shelter.shelter_id == shelter_phone.shelter_id)
        .all()
    )
    title='收容所資訊'
    return render_template('page9.html',title=title, shelter_data=shelter_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    title = '我要登入'
    if request.method == 'POST':
        # Handle form submission here
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            login_user(user)
            flash('登入成功！', 'success')
            return redirect(url_for('index'))
        else:
            flash('登入失敗，請檢查您的帳號和密碼。', 'error')
    
    return render_template('page4.html', title=title)

# Example logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('登出成功！', 'success')
    return redirect(url_for('index'))
@app.route('/dashboard', methods = ['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        selected_option = request.form.get('select_option')
        if selected_option=="option1":
            return redirect(url_for('update'))
        if selected_option=="option2":
            return redirect(url_for('index'))
    # stray animals
    stray_alias = aliased(stray_ani)
    species_alias = aliased(speciesTable)
    color_alias = aliased(colorTable)
    region_alias = aliased(regionTable)
    city_alias = aliased(cityTable)
    breed_alias = aliased(breedTable)
    stray = (
        db.session.query(stray_alias.solved, stray_alias.stray_gender, stray_alias.date, species_alias.species_name, color_alias.color_name, region_alias.region_name, city_alias.city_name, breed_alias.breed_name)
       .join(species_alias, stray_alias.species_id == species_alias.species_id)
       .join(color_alias, stray_alias.color_id == color_alias.color_id)
       .join(region_alias, stray_alias.region_id == region_alias.region_id)
       .join(city_alias, stray_alias.city_id == city_alias.city_id)
       .join(breed_alias, stray_alias.breed_id == breed_alias.breed_id)
    )
    stray = stray.filter(stray_alias.user_email == current_user.email)
    request_stray = stray.all()
    
    # found animals
    found_alias = aliased(found_ani)
    found = (
        db.session.query(found_alias.found_id, found_alias.solved, found_alias.found_gender, found_alias.date, species_alias.species_name, color_alias.color_name, region_alias.region_name, city_alias.city_name, breed_alias.breed_name)
       .join(species_alias, found_alias.species_id == species_alias.species_id)
       .join(color_alias, found_alias.color_id == color_alias.color_id)
       .join(region_alias, found_alias.region_id == region_alias.region_id)
       .join(city_alias, found_alias.city_id == city_alias.city_id)
       .join(breed_alias, found_alias.breed_id == breed_alias.breed_id)
    )
    found = found.filter(found_alias.user_email == current_user.email)
    request_found = found.all()
    title = "過往提交紀錄"
    
    return render_template('page7.html', request_stray = request_stray, request_found = request_found, current_user = current_user, title = title)


###################################################################################################################################
@app.route('/update', methods = ['GET', 'POST'])
@login_required
def update():
    title = "更新走失動物解決狀態"
    if request.method == 'POST':
        selected_option = request.form.get('selection')
        if selected_option=="back":
            return redirect(url_for('dashboard'))
    
    stray_alias = aliased(stray_ani)
    species_alias = aliased(speciesTable)
    color_alias = aliased(colorTable)
    region_alias = aliased(regionTable)
    city_alias = aliased(cityTable)
    breed_alias = aliased(breedTable)
    stray = (
        db.session.query(stray_alias.stray_id, stray_alias.solved, stray_alias.stray_gender, stray_alias.date, species_alias.species_name, color_alias.color_name, region_alias.region_name, city_alias.city_name, breed_alias.breed_name)
    .join(species_alias, stray_alias.species_id == species_alias.species_id)
    .join(color_alias, stray_alias.color_id == color_alias.color_id)
    .join(region_alias, stray_alias.region_id == region_alias.region_id)
    .join(city_alias, stray_alias.city_id == city_alias.city_id)
    .join(breed_alias, stray_alias.breed_id == breed_alias.breed_id)
    )
    stray = stray.filter(stray_alias.user_email == current_user.email, (stray_alias.solved == 'no' or stray_alias.solved == '否'))
    request_stray = stray.all()
    if request.method == 'POST':
        select_ani = request.form.get('done')
        # if(select_ani):
        st = stray_ani.query.filter_by(stray_id = select_ani).first()
        if st:
            st.solved = "yes"
            db.session.flush()
            db.session.commit()
        return redirect(url_for('update_success'))
    return render_template('change_condition.html', request_stray = request_stray,  current_user = current_user, title = title)

#################################################################################################



@app.route('/register', methods=['GET', 'POST'])
def register():
    title = '我要註冊'
    city_names = cityTable.query.all()
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        gender = request.form.get('select-gender')
        city_id = int(request.form.get('select-city'))
        # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash('此email已經存在，無法建立使用者。', 'error')
            return redirect(url_for('register_failed'))
        else:
            # Create a new user and add to the database
            new_user = User(account_name=name, email=email, password=password, phone=phone, gender=gender, city_id=city_id)
            db.session.add(new_user)
            db.session.commit()

            # Log in the new user
            login_user(new_user)

            # Optionally, you can redirect to a different page after successful registration
            flash('註冊成功！', 'success')
            return redirect(url_for('dashboard'))

    return render_template('page5.html', title=title,city_names=city_names)

@app.route('/submission_success', methods=['GET', 'POST'])
def submission_success():
    title='感謝您的申報!'
    if request.method == 'POST':
        selected_option = request.form.get('select_option')
        if selected_option == 'option1':
            return redirect(url_for('index'))
    return render_template('page6.html', title=title)

@app.route('/update_success', methods=['GET', 'POST'])
def update_success():
    title='感謝您的更新!'
    if request.method == 'POST':
        selected_option = request.form.get('select_option')
        if selected_option == 'option1':
            return redirect(url_for('index'))
    return render_template('page6.html', title=title)

@app.route('/register_failed', methods=['GET', 'POST'])
def register_failed():
    title='此電子郵件已註冊過!'
    if request.method == 'POST':
        selected_option = request.form.get('select_option')
        if selected_option == 'option1':
            return redirect(url_for('index'))
    return render_template('page8.html', title=title)

@app.route('/submit_form', methods=['POST'])
def submit_form():
    select_type = request.form.get('select-type')
    select_spieces = request.form.get('select-spieces')
    select_breed = request.form.get('select-breed')
    select_color = request.form.get('select-color')
    select_gender = request.form.get('select-gender')
    select_resolved = request.form.get('select-resolved')
    select_city = request.form.get('select-city')
    select_area = request.form.get('select-area')
    select_date = request.form.get('select-date')
    select_email = current_user.email
    
    if(select_type == "lost"):
        stray_count = db.session.query(func.count(stray_ani.stray_id)).scalar()
        st_id = stray_count + 1
        stray = stray_ani(stray_id = st_id, color_id = select_color, region_id = select_area, city_id = select_city, date = select_date, 
                          stray_gender = select_gender, solved = select_resolved, species_id = select_spieces, breed_id = select_breed, user_email = select_email)
        db.session.add(stray)
        db.session.commit()
        return redirect(url_for('submission_success'))
        
    elif(select_type == "found"):
        found_count = db.session.query(func.count(found_ani.found_id)).scalar()
        fo_id = found_count + 1
        
        found = found_ani(found_id = fo_id, color_id = select_color, region_id = select_area, city_id = select_city, date = select_date, 
                          found_gender = select_gender, solved = select_resolved, species_id = select_spieces, breed_id = select_breed, 
                           user_email = select_email)
        db.session.add(found)
        db.session.commit()
        return redirect(url_for('submission_success'))

    
    return f"Form submitted successfully with values: {select_type}, {select_spieces}, {select_breed}, {select_color}, {select_gender}, {select_resolved}, {select_city}, {select_area}, {select_date}"



if __name__ == '__main__':
    app.run(debug=True)
