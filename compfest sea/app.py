from datetime import datetime, timedelta
from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
import bleach

app = Flask(__name__)
bcrypt = Bcrypt(app)

csrf = CSRFProtect(app)
csrf.init_app(app)

app.config['SECRET_KEY'] = 'a66784bea5d159ff575673ceb0ea4aafa70ce8324276e4ed41f6262ab3a86532'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes = 10)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'User'
    Email = db.Column(db.String(64), primary_key=True)
    Name = db.Column(db.String(64), nullable=False)
    Password = db.Column(db.String(64), nullable=False)
    Role = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return f"User('{self.Email}')"

class Subscription(db.Model):
    __tablename__ = 'Subscription'
    SubscriptionID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(64), nullable=False)
    PhoneNumber = db.Column(db.String(32), nullable=False)
    PlanSelection = db.Column(db.String(32), nullable=False)
    MealType = db.Column(db.Text, nullable=False)
    DeliveryDays = db.Column(db.Text, nullable=False)
    Allergies = db.Column(db.Text)
    Prices = db.Column(db.Integer, nullable=False)
    Status = db.Column(db.String(32), nullable=False)
    SubscriptionTime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    def __repr__(self):
        return f"Subscription('{self.SubscriptionID}', '{self.Name}')"
    
class Modify(db.Model):
    __tablename__ = 'Modify'
    ModifyID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    SubscriptionID = db.Column(db.Integer, db.ForeignKey('Subscription.SubscriptionID'), nullable=False)
    CancelTime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    ReactivateTime = db.Column(db.DateTime)
    Status = db.Column(db.String(32), nullable=False)
    # Subscription = db.relationship('Subscription', backref='subsid', lazy=True)

    def __repr__(self):
        return f"Subscription('{self.ModifyID}', '{self.SubscriptionID}')"

class MealPlan(db.Model):
    __tablename__ = 'MealPlan'
    MealPlanID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    MealPlanName = db.Column(db.String(128), nullable=False)
    ShortDes = db.Column(db.String(128), nullable=False)
    Price = db.Column(db.String(128), nullable=False)
    Description = db.Column(db.Text, nullable=False)
    NutritionalInfo = db.Column(db.Text, nullable=False)
    Allergens = db.Column(db.Text, nullable=False)
    Tags = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Subscription('{self.MealPlanID}', '{self.MealPlanName}')"

class Testimonial(db.Model):
    __tablename__ = 'Testimonial'
    TestimonialID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(64), nullable=False)
    Rating = db.Column(db.Integer, nullable=False)
    ReviewMessage = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Subscription('{self.TestimonialID}', '{self.Name}')"

@app.route('/', methods = ['POST', 'GET'])
def home():
    if 'email' in session:
        if session['role'] == 'user':
            if request.method == 'POST':
                name = bleach.clean(request.form.get('Name'), strip=True)
                rating = bleach.clean(request.form.get('Rating'), strip=True)
                review = bleach.clean(request.form.get('ReviewMessage'), strip=True)

                if name != User.query.filter_by(Email=session['email']).first().Name:
                    flash(bleach.clean('Please input the same name as profile username!', strip=True))
                    return render_template("home.html", testimonial=testimonial)
                
                testimoni = Testimonial(Name=name, Rating=rating, ReviewMessage=review)
                db.session.add(testimoni)
                db.session.commit()

                flash(bleach.clean('Thank you for your testimonial!', strip=True))
        
    testimonial = Testimonial.query.all()
    return render_template("home.html", testimonial=testimonial)

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if 'email' in session:
        flash(bleach.clean('You are already logged in!', strip=True))
        return redirect(url_for('home'))

    if request.method == 'GET':
        return render_template("login.html")
    
    email = bleach.clean(request.form.get('Email'), strip=True)
    password = bleach.clean(request.form.get('Password'), strip=True)
    user = User.query.filter_by(Email=email).first()

    if not user or not bcrypt.check_password_hash(user.Password, password):
        flash(bleach.clean('Please check your login details and try again!', strip=True))
        return render_template('login.html')
    
    session['email'] = email
    session['role'] = user.Role
    session.permanent = True
    return redirect(url_for('home'))

@app.route('/register', methods = ['POST', 'GET'])
def register():
    if 'email' in session:
        flash(bleach.clean('You are already logged in!', strip=True))
        return redirect(url_for('home'))
    
    if request.method == 'GET':
        return render_template("register.html")
    
    name = bleach.clean(request.form.get('Name'), strip=True)
    email = bleach.clean(request.form.get('Email'), strip=True)
    password = bcrypt.generate_password_hash(bleach.clean(request.form.get('Password'), strip=True)).decode('utf-8')

    if User.query.filter_by(Email=email).first():
        flash(bleach.clean('Email has been used. Try other email!', strip=True))
        return render_template('register.html')
    
    user = User(Email=email, Name=name, Password=password, Role=bleach.clean('user', strip=True))
    db.session.add(user)
    db.session.commit()

    flash(bleach.clean('Your data has been added. Please Login!', strip=True))
    return redirect(url_for('login'))

@app.route('/meal')
def meal():
    meals = MealPlan.query.all()
    nutriinfo = []
    allergens = []
    tags = []
    idx = 1
    for meal in meals:
        nutri = [idx]
        allergen = [idx]
        tag = [idx]

        nutri.extend(meal.NutritionalInfo.split('.'))
        allergen.extend(meal.Allergens.split(','))
        tag.extend(meal.Tags.split(','))

        nutriinfo.append(nutri)
        allergens.append(allergen)
        tags.append(tag)
        idx += 1
        
    return render_template("meal.html", meals=meals, nutriinfo=nutriinfo, allergens=allergens, tags=tags)

@app.route('/subscription', methods = ['POST', 'GET'])
def subscription():
    if 'email' in session:
        if session['role'] == 'user':
            if request.method == 'GET':
                return render_template("subscription.html")
        
            name = bleach.clean(request.form.get('Name'), strip=True)
            phone = bleach.clean(request.form.get('PhoneNumber'), strip=True)
            plan = bleach.clean(request.form.get('Plan'), strip=True)
            types = request.form.getlist('Time')
            days = request.form.getlist('Day')
            allergies = bleach.clean(request.form.get('Allergies'), strip=True)
            status = bleach.clean('active', strip=True)

            if name != User.query.filter_by(Email=session['email']).first().Name:
                flash(bleach.clean('Please input the same name as profile username!', strip=True))
                return render_template("subscription.html")
            
            if plan == 'Diet Plan':
                price = 30000 * len(types) * len(days) * 4.3
            elif plan == 'Protein Plan':
                price = 40000 * len(types) * len(days) * 4.3
            else:
                price = 60000 * len(types) * len(days) * 4.3

            user = Subscription(Name=name, PhoneNumber=phone, PlanSelection=plan, MealType=', '.join(types), DeliveryDays=', '.join(days), Allergies=allergies, Prices=price, Status=status)
            db.session.add(user)
            db.session.commit()

            flash(bleach.clean('You have successfully subscribe a new meal plan!', strip=True))
            return redirect(url_for('home'))
        
        flash(bleach.clean('You are an admin. Please login as a user to subscribe!', strip=True))
        return redirect(url_for('home'))
    
    flash(bleach.clean('Please login before subscribing!', strip=True))
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        return render_template("user.html")
    
    flash('Please login to access your account!')
    return redirect(url_for('login')) 

@app.route('/profile')
def profile():
    if 'email' in session:
        user = User.query.filter_by(Email=session['email']).first()
        return render_template("profile.html", user=user)
    
    flash(bleach.clean('Please login to access your account!', strip=True))
    return redirect(url_for('login')) 

@app.route('/view-subscription')
def viewSubscription():
    if 'email' in session:
        if session['role'] == 'user':
            name = User.query.filter_by(Email=session['email']).first().Name
            subscriptions = Subscription.query.filter_by(Name=name).all()

            if not subscriptions:
                flash(bleach.clean('There is no subscription have been made. Please subscribe to see your subscription!', strip=True))
                return redirect(url_for('subscription'))
            
            items = []
            for subscription in subscriptions:
                if subscription.Status == 'active':
                    items.append(subscription)
            
            if items:
                return render_template("view-subscription.html", subscriptions=items)
            
            flash(bleach.clean('All of your subscriptions are inactive. Please Reactivate to see your subscription!', strip=True))
            return redirect(url_for('dashboard'))
        
        flash(bleach.clean('You are an admin. Please login as a user to subscribe!', strip=True))
        return redirect(url_for('dashboard'))
    
    flash(bleach.clean('Please login before subscribing!', strip=True))
    return redirect(url_for('login'))

@app.route('/pause-subscription')
def pausesubscription():
    if 'email' in session:
        if session['role'] == 'user':
            name = User.query.filter_by(Email=session['email']).first().Name
            subscriptions = Subscription.query.filter_by(Name=name).all()

            if not subscriptions:
                flash(bleach.clean('There is no subscription have been made. Please subscribe to manage your subscription!', strip=True))
                return redirect(url_for('subscription'))
            
            items = []
            for subscription in subscriptions:
                if subscription.Status == 'active':
                    items.append(subscription)
            
            if items:
                return render_template("pause-subscription.html", subscriptions=items)
            
            flash(bleach.clean('All of your subscriptions are inactive. Please Reactivate to manage your subscription!', strip=True))
            return redirect(url_for('dashboard'))
        
        flash(bleach.clean('You are an admin. Please login as a user to subscribe!', strip=True))
        return redirect(url_for('dashboard'))
    
    flash(bleach.clean('Please login before subscribing!', strip=True))
    return redirect(url_for('login'))

@app.route('/pause-subscription/<int:SubscriptionID>', methods=['POST'])
def pauseSubscription(SubscriptionID):
    if 'email' in session:
        if session['role'] == 'user':
            subscription = Subscription.query.get_or_404(SubscriptionID)
            subscription.Status = bleach.clean('inactive', strip=True)

            modification = Modify(SubscriptionID=SubscriptionID, Status=bleach.clean('pause', strip=True))
            db.session.add(modification)
            
            db.session.commit()
            
            flash(bleach.clean('You have successfully pause your subscription!', strip=True))
            return redirect(url_for('dashboard'))

        flash(bleach.clean('You are an admin. Please login as a user to subscribe!', strip=True))
        return redirect(url_for('dashboard'))
    
    flash(bleach.clean('Please login before subscribing!', strip=True))
    return redirect(url_for('login'))

@app.route('/reactivate-subscription')
def reactivatesubscription():
    if 'email' in session:
        if session['role'] == 'user':
            name = User.query.filter_by(Email=session['email']).first().Name
            subscriptions = Subscription.query.filter_by(Name=name).all()

            if not subscriptions:
                flash(bleach.clean('There is no subscription have been made. Please subscribe to manage your subscription!', strip=True))
                return redirect(url_for('subscription'))

            items = []
            for subscription in subscriptions:
                if subscription.Status == 'inactive':
                    items.append(subscription)
            
            if items:
                return render_template("reactivate-subscription.html", subscriptions=items)
            
            flash(bleach.clean('All of your subscriptions are active!', strip=True)) 
            return redirect(url_for('dashboard'))
        
        flash(bleach.clean('You are an admin. Please login as a user to subscribe!', strip=True))
        return redirect(url_for('dashboard'))
    
    flash(bleach.clean('Please login before subscribing!', strip=True))
    return redirect(url_for('login'))

@app.route('/reactivate-subscription/<int:SubscriptionID>', methods=['POST'])
def reactivateSubscription(SubscriptionID):
    if 'email' in session:
        if session['role'] == 'user':
            subscription = Subscription.query.get_or_404(SubscriptionID)
            subscription.Status = bleach.clean('active', strip=True)

            modification = Modify.query.filter_by(SubscriptionID=SubscriptionID).first_or_404()
            modification.ReactivateTime = datetime.utcnow()
            modification.Status = bleach.clean('reactive', strip=True)
            
            db.session.commit()
            
            flash(bleach.clean('You have successfully reactivate your subscription!', strip=True))
            return redirect(url_for('dashboard'))

        flash(bleach.clean('You are an admin. Please login as a user to subscribe!', strip=True))
        return redirect(url_for('dashboard'))
    
    flash(bleach.clean('Please login before subscribing!', strip=True))
    return redirect(url_for('login'))

@app.route('/cancel-subscription')
def cancelsubscription():
    if 'email' in session:
        if session['role'] == 'user':
            name = User.query.filter_by(Email=session['email']).first().Name
            subscriptions = Subscription.query.filter_by(Name=name).all()

            if not subscriptions:
                flash(bleach.clean('There is no subscription have been made. Please subscribe to manage your subscription!', strip=True))
                return redirect(url_for('subscription'))
            
            items = []
            for subscription in subscriptions:
                if subscription.Status!= 'cancel':
                    items.append(subscription)

            return render_template("cancel-subscription.html", subscriptions=items)
        
        flash(bleach.clean('You are an admin. Please login as a user to subscribe!', strip=True))
        return redirect(url_for('dashboard'))
    
    flash(bleach.clean('Please login before subscribing!', strip=True))
    return redirect(url_for('login'))

@app.route('/cancel-subscription/<int:SubscriptionID>', methods=['POST'])
def cancelSubscription(SubscriptionID):
    if 'email' in session:
        if session['role'] == 'user':
            # modification = Modify.query.filter_by(SubscriptionID=SubscriptionID).first()
            # if modification:
            #     db.session.delete(modification)
            
            subscription = Subscription.query.get_or_404(SubscriptionID)
            subscription.Status = 'cancel'
            
            db.session.commit()
            
            flash(bleach.clean('You have successfully cancel your subscription!', strip=True))
            return redirect(url_for('dashboard'))

        flash(bleach.clean('You are an admin. Please login as a user to subscribe!', strip=True))
        return redirect(url_for('dashboard'))
    
    flash(bleach.clean('Please login before subscribing!', strip=True))
    return redirect(url_for('login'))

@app.route('/new-subscriptions', methods=['POST', 'GET'])
def newSubscriptions():
    subscriptions = None
    if 'email' in session:
        if session['role'] == 'admin':
            if request.method == 'POST':
                start = datetime.strptime(bleach.clean(request.form.get('start_date'), strip=True), "%Y-%m-%dT%H:%M")
                end = datetime.strptime(bleach.clean(request.form.get('end_date'), strip=True), "%Y-%m-%dT%H:%M")

                if start > end:
                    flash(bleach.clean('The date is not valid!', strip=True))
                    return redirect(url_for('newSubscriptions'))
                
                subscriptions = Subscription.query.filter(Subscription.SubscriptionTime.between(start, end)).all()
                if not subscriptions:
                    flash(bleach.clean('There is no subscription in selected date!', strip=True))
                    return redirect(url_for('newSubscriptions'))
                
            return render_template("new-subscriptions.html", subscriptions=subscriptions)
        
        flash(bleach.clean('You are a user. Please login as an admin to access!', strip=True))
        return redirect(url_for('dashboard'))
    
    flash(bleach.clean('Please login before accesssing!', strip=True))
    return redirect(url_for('login'))

@app.route('/monthly-recurring-revenue', methods=['POST', 'GET'])
def monthlyRecurringRevenue():
    amount = None
    subscriptions = None
    items = None
    if 'email' in session:
        if session['role'] == 'admin':
            if request.method == 'POST':
                start = datetime.strptime(bleach.clean(request.form.get('start_date'), strip=True), "%Y-%m-%dT%H:%M")
                end = datetime.strptime(bleach.clean(request.form.get('end_date'), strip=True), "%Y-%m-%dT%H:%M")

                if start > end:
                    flash(bleach.clean('The date is not valid!', strip=True))
                    return redirect(url_for('monthlyRecurringRevenue'))
                
                subscriptions = Subscription.query.filter(Subscription.SubscriptionTime.between(start, end)).all()
                if not subscriptions:
                    flash(bleach.clean('There is no subscription in selected date!', strip=True))
                    return redirect(url_for('monthlyRecurringRevenue'))
                
                amount = 0
                items = []
                for subscription in subscriptions:
                    if subscription.Status == 'active':
                        amount += subscription.Prices
                        items.append(subscription)
                
            return render_template("monthly-recurring-revenue.html", subscriptions=items, amount=amount)
        
        flash(bleach.clean('You are a user. Please login as an admin to access!', strip=True))
        return redirect(url_for('dashboard'))
    
    flash(bleach.clean('Please login before accesssing!', strip=True))
    return redirect(url_for('login'))

@app.route('/reactivations', methods=['POST', 'GET'])
def reactivations():
    subscriptions = None
    if 'email' in session:
        if session['role'] == 'admin':
            if request.method == 'POST':
                start = datetime.strptime(bleach.clean(request.form.get('start_date'), strip=True), "%Y-%m-%dT%H:%M")
                end = datetime.strptime(bleach.clean(request.form.get('end_date'), strip=True), "%Y-%m-%dT%H:%M")

                if start > end:
                    flash(bleach.clean('The date is not valid!', strip=True))
                    return redirect(url_for('reactivations'))
                
                pauses = Modify.query.filter(Modify.CancelTime.between(start, end)).all()
                reactivates = Modify.query.filter(Modify.ReactivateTime.between(start, end)).all()
                if not pauses or not reactivates:
                    flash(bleach.clean('There is no subscription in selected date!', strip=True))
                    return redirect(url_for('reactivations'))
                
                subscriptions = []
                for pause in pauses:
                    for reactivate in reactivates:
                        if pause.ModifyID == reactivate.ModifyID:
                            subscriptions.append(pause)
            
            return render_template("reactivations.html", subscriptions=subscriptions)
        
        flash(bleach.clean('You are a user. Please login as an admin to access!', strip=True))
        return redirect(url_for('dashboard'))
    
    flash(bleach.clean('Please login before accesssing!', strip=True))
    return redirect(url_for('login'))

@app.route('/subscription-growth')
def subscriptionGrowth():
    if 'email' in session:
        if session['role'] == 'admin':
            subscriptions = Subscription.query.filter_by(Status='active').all()
            
            if not subscriptions:
                flash(bleach.clean('There is no active subscription!', strip=True)) 
                return redirect(url_for('dashboard'))
            
            items = []
            for subscription in subscriptions:
                if subscription.Status == 'active':
                    items.append(subscription)

            return render_template("subscription-growth.html", subscriptions=items)
        
        flash(bleach.clean('You are a user. Please login as an admin to access!', strip=True))
        return redirect(url_for('dashboard'))
    
    flash(bleach.clean('Please login before accesssing!', strip=True))
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('email', default=None)
    session.pop('role', default=None)
    flash(bleach.clean('You were logged out!', strip=True))
    return redirect(url_for('login'))

@app.route('/contact')
def contact():
    return render_template("contact.html")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        des1 = '''At its heart lies tender, marinated chicken breast, grilled to perfection for a slightly smoky flavor and juicy texture.
            It's served at top of a bed of fluffy quinoa, a super grain rich in protein and fiber, paired with a vibrant medley of oven-roasted bell peppers, steamed broccoli florets, and lightly caramelized onions.
            The dish is finished with a zesty honey-lime vinaigrette, adding a tangy-sweet lift that ties the ingredients together.
            Designed for active individuals, this meal offers long-lasting energy without heaviness, ideal for lunch or post-workout recovery.'''
        nutri1 = '''Serving Size - 400 gram. 🔥 Calories - 420 kcal. 🥩 Protein - 38 gram. 🍚 Carbohydrates - 35 gram. 🍯 Sugars - 5 gram. 🥑 Fat - 12 gram. 🥬 Fiber - 6 gram. 🧂 Sodium - 310 miligram. 🍊 Vitamins - rich in Vitamin B6 and C'''
        meal1 = MealPlan(MealPlanName=bleach.clean('Grilled Chicken Quinoa Bowl', strip=True), ShortDes=bleach.clean('with Roasted Bell Peppers, Broccoli, and Honey-Lime Dressing', strip=True), Price=bleach.clean('Rp 47.000,00', strip=True), Description=bleach.clean(des1, strip=True), NutritionalInfo=bleach.clean(nutri1, strip=True), Allergens=bleach.clean('None', strip=True), Tags=bleach.clean('Protein Smart, Calorie Smart, Fiber Smart, Low Sugar, Gluten-Free, Dairy-Free', strip=True))
        
        des2 = '''Flavor-rich Japanese-inspired dish designed for those seeking a well-balanced and protein-dense meal. 
            Featuring a thick fillet of Atlantic salmon, delicately grilled and glazed with a homemade light teriyaki sauce made from low-sodium soy, garlic, and a touch of honey.
            Served with a side of steamed brown rice and a colorful medley of stir-fried vegetables—carrots, bok choy, and shiitake mushrooms—this bento box offers a rich umami experience without excess sodium or sugar.
            The bento is finished with a sprinkle of sesame seeds and chopped scallions for a fresh, aromatic finish.'''
        nutri2 = '''Serving Size - 450 gram. 🔥 Calories - 480 kcal. 🥩 Protein - 32 gram. 🍚 Carbohydrates - 40 gram. 🍯 Sugars - 8 gram. 🥑 Fat - 18 gram. 🥬 Fiber - 5 gram. 🧂 Sodium - 520 miligram. 🍊 Vitamins - rich in Vitamin A, B12, C, and D'''
        meal2 = MealPlan(MealPlanName=bleach.clean('Salmon Teriyaki Bento', strip=True), ShortDes=bleach.clean('Salmon Teriyaki-Glazed, with Brown Rice and Stir-Fried Vegetables', strip=True), Price=bleach.clean('Rp 65.000,00', strip=True), Description=bleach.clean(des2, strip=True), NutritionalInfo=bleach.clean(nutri2, strip=True), Allergens=bleach.clean('Soy, Fish, Sesame, Gluten', strip=True), Tags=bleach.clean('Protein Smart, Omega-3 Rich, Fiber Smart, Low Sugar, Dairy-Free', strip=True))
        
        des3 = '''A plant-powered, high-protein bowl designed for clean energy and vibrant nutrition, features firm tofu cubes, pan-seared to golden perfection and tossed in a garlic-ginger soy sauce glaze, delivering that savory umami punch without overpowering saltiness.
            Accompanied by a colorful medley of seasonal vegetables like bok choy, carrots, red bell peppers, and snap peas, all stir-fried lightly in sesame oil to preserve their crunch and nutrients.
            Served over a small bed of red rice or brown rice, this bowl is light, filling, and completely plant-based.
            Ideal for anyone seeking a vegan, high-protein, fiber-rich, and low-cholesterol meal option.'''
        nutri3 = '''Serving Size - 400 gram. 🔥 Calories - 370 kcal. 🥩 Protein - 22 gram. 🍚 Carbohydrates - 33 gram. 🍯 Sugars - 6 gram. 🥑 Fat - 15 gram. 🥬 Fiber - 7 gram. 🧂 Sodium - 469 miligram. 🍊 Vitamins - rich in Vitamin A, B1, C, and K'''
        meal3 = MealPlan(MealPlanName=bleach.clean('Tofu Veggie Stir Fry', strip=True), ShortDes=bleach.clean('Tofu with Sautéed Vegetables and Garlic-Ginger Sauce', strip=True), Price=bleach.clean('Rp 34.000,00', strip=True), Description=bleach.clean(des3, strip=True), NutritionalInfo=bleach.clean(nutri3, strip=True), Allergens=bleach.clean('Soy, Sesame, Gluten', strip=True), Tags=bleach.clean('Protein Smart, Vegan Friendly, Fiber Smart, Low Glycemic, Dairy-Free', strip=True))
        
        des4 = '''This meal features slices of marinated tempeh, grilled until golden and slightly crisp on the edges, seasoned with a blend of Mediterranean herbs like thyme, rosemary, and oregano.
                The tempeh is layered with crisp lettuce, sliced tomatoes, cucumber, and a spoonful of house-made herbed yogurt sauce, all wrapped inside a whole wheat tortilla.
                The sauce adds a creamy tang with fresh mint and lemon undertones, making this wrap a nutrient-packed option perfect for lunch or a light dinner.'''
        nutri4 = '''Serving Size - 350 gram. 🔥 Calories - 400 kcal. 🥩 Protein - 25 gram. 🍚 Carbohydrates - 35 gram. 🍯 Sugars - 5 gram. 🥑 Fat - 13 gram. 🥬 Fiber - 6 gram. 🧂 Sodium - 420 miligram. 🍊 Vitamins - rich in Vitamin A, B1, C, and K'''
        meal4 = MealPlan(MealPlanName=bleach.clean('Herbed Grilled Tempeh Wrap', strip=True), ShortDes=bleach.clean('Grilled Tempeh Wrapped with Lettuce, Tomato, and Herbed Yogurt in Whole Wheat Wrap', strip=True), Price=bleach.clean('Rp 36.000,00', strip=True), Description=bleach.clean(des4, strip=True), NutritionalInfo=bleach.clean(nutri4, strip=True), Allergens=bleach.clean('Soy, Dairy, Gluten', strip=True), Tags=bleach.clean('Protein Smart, Vegetarian, Fiber Smart', strip=True))
        
        des5 = '''This box features grilled chicken satay skewers, marinated in aromatic spices and herbs, then grilled over an open flame for charred edges and juicy tenderness.
                It's paired with a lightly sweet and spicy peanut sauce, made with natural peanut butter, coconut milk, garlic, and chili.
                On the side: a refreshing cucumber and red onion salad with a touch of lime for acidity, and a creamy, nutrient-dense sweet potato mash, lightly seasoned with olive oil and sea salt.
                This meal is designed to fuel your day with lean protein, complex carbs, and healthy fats — perfect for gym-goers or those seeking sustained energy.'''
        nutri5 = '''Serving Size - 420 gram. 🔥 Calories - 510 kcal. 🥩 Protein - 35 gram. 🍚 Carbohydrates - 28 gram. 🍯 Sugars - 6 gram. 🥑 Fat - 22 gram. 🥬 Fiber - 5 gram. 🧂 Sodium - 540 miligram. 🍊 Vitamins - rich in Vitamin A, B1, C, and E'''
        meal5 = MealPlan(MealPlanName=bleach.clean('Chicken Satay Protein Box', strip=True), ShortDes=bleach.clean('Grilled Chicken Skewers with Peanut Sauce, Cucumber Salad, and Sweet Potato Mash', strip=True), Price=bleach.clean('Rp 42.000,00', strip=True), Description=bleach.clean(des5, strip=True), NutritionalInfo=bleach.clean(nutri5, strip=True), Allergens=bleach.clean('Soy, Peanut, Gluten', strip=True), Tags=bleach.clean('Protein Smart, Calorie Smart, Fiber Smart, Low Sugar', strip=True))
        
        des6 = '''A deeply flavorful and aromatic Indonesian classic, Pepes Ikan features fresh white fish (typically mackerel or snapper) marinated in a rich blend of traditional spices-turmeric, lemongrass, garlic, chili, and kaffir lime leaves.
                The fish is then wrapped in banana leaves and steamed or grilled, allowing the spices to infuse while keeping the dish moist and oil-free.
                It's served with a portion of red rice, known for its higher fiber and lower glycemic index compared to white rice, and a side of blanched lemon basil (kemangi) or sautéed vegetables.'''
        nutri6 = '''Serving Size - 400 gram. 🔥 Calories - 430 kcal. 🥩 Protein - 34 gram. 🍚 Carbohydrates - 38 gram. 🍯 Sugars - 3 gram. 🥑 Fat - 12 gram. 🥬 Fiber - 5 gram. 🧂 Sodium - 450 miligram. 🍊 Vitamins - rich in Vitamin A, B12, C, and D'''
        meal6 = MealPlan(MealPlanName=bleach.clean('Pepes Ikan', strip=True), ShortDes=bleach.clean('Steamed Spiced Mackerel in Banana Leaf with Red Rice and Lemon Basil', strip=True), Price=bleach.clean('Rp 37.000,00', strip=True), Description=bleach.clean(des6, strip=True), NutritionalInfo=bleach.clean(nutri6, strip=True), Allergens=bleach.clean('Fish', strip=True), Tags=bleach.clean('Protein Smart, Fiber Smart, Gluten-Free, Dairy-Free', strip=True))
        
        des7 = '''This bold and aromatic dish hails from Manado, North Sulawesi, and features chicken simmered in a vibrant yellow spice blend known as woku.
                Made from turmeric, chili, lemongrass, and lime leaves, ayam woku is fragrant, slightly spicy, and full of herbal depth.
                It's served with red rice (nasi merah) for added fiber and minerals, and accompanied by a side of sautéed leafy greens such as water spinach (kangkung) or cassava leaves (daun singkong), lightly cooked with garlic.'''
        nutri7 = '''Serving Size - 420 gram. 🔥 Calories - 460 kcal. 🥩 Protein - 36 gram. 🍚 Carbohydrates - 38 gram. 🍯 Sugars - 4 gram. 🥑 Fat - 14 gram. 🥬 Fiber - 5 gram. 🧂 Sodium - 510 miligram. 🍊 Vitamins - rich in Vitamin A, B6, and C'''
        meal7 = MealPlan(MealPlanName=bleach.clean('Woku Chicken', strip=True), ShortDes=bleach.clean('Spicy Manado-style Chicken Stew with Red Rice and Sautéed Water Spinach', strip=True), Price=bleach.clean('Rp 45.000,00', strip=True), Description=bleach.clean(des7, strip=True), NutritionalInfo=bleach.clean(nutri7, strip=True), Allergens=bleach.clean('None', strip=True), Tags=bleach.clean('Protein Smart, Fiber Smart, Gluten-Free, Dairy-Free', strip=True))
        
        des8 = '''A light, comforting, and immune-boosting dish made with free-range chicken (ayam kampung) simmered slowly in a clear broth with carrots, potatoes, young corn, celery, and shallots.
                Unlike creamy or heavy soups, it is all about clarity and purity—flavored with simple aromatics like white pepper, garlic, and a touch of nutmeg.
                Served warm with a side of red rice or as a standalone soup, it's ideal for a low-calorie, hydrating meal, commonly enjoyed across Indonesia as a healthy home remedy or post-illness comfort food.'''
        nutri8 = '''Serving Size - 400 gram. 🔥 Calories - 310 kcal. 🥩 Protein - 26 gram. 🍚 Carbohydrates - 22 gram. 🍯 Sugars - 3 gram. 🥑 Fat - 9 gram. 🥬 Fiber - 4 gram. 🧂 Sodium - 420 miligram. 🍊 Vitamins - rich in Vitamin A, B6, C, and K'''
        meal8 = MealPlan(MealPlanName=bleach.clean('Clear Chicken Soup', strip=True), ShortDes=bleach.clean('Clear Chicken and Vegetable Soup with Young Corn, Carrots, and Celery', strip=True), Price=bleach.clean('Rp 50.000,00', strip=True), Description=bleach.clean(des8, strip=True), NutritionalInfo=bleach.clean(nutri8, strip=True), Allergens=bleach.clean('None', strip=True), Tags=bleach.clean('Low Calorie, Immune Boosting, Gluten-Free, Dairy-Free', strip=True))

        des9 = '''A wholesome and vibrant plant-based Indonesian classic, it consists of a generous medley of lightly steamed vegetables—such as spinach, long beans, bean sprouts, and cabbage—tossed with urap, a traditional mixture of grated coconut, garlic, kaffir lime leaves, and chili.
                Served alongside grilled tempeh marinated in a sweet-savory glaze, this meal is packed with fiber, plant protein, and rich Indonesian flavors.
                It's perfect for vegetarians, vegans, or anyone looking for a deeply satisfying yet clean and nutritious local option.'''
        nutri9 = '''Serving Size - 400 gram. 🔥 Calories - 390 kcal. 🥩 Protein - 21 gram. 🍚 Carbohydrates - 28 gram. 🍯 Sugars - 6 gram. 🥑 Fat - 18 gram. 🥬 Fiber - 8 gram. 🧂 Sodium - 440 miligram. 🍊 Vitamins - rich in Vitamin A, C, and K'''
        meal9 = MealPlan(MealPlanName=bleach.clean('Urap Sayur with Tempe Bakar', strip=True), ShortDes=bleach.clean('Steamed Vegetables with Seasoned Grated Coconut, paired with Grilled Tempeh', strip=True), Price=bleach.clean('Rp 33.000,00', strip=True), Description=bleach.clean(des9, strip=True), NutritionalInfo=bleach.clean(nutri9, strip=True), Allergens=bleach.clean('Soy, Coconut', strip=True), Tags=bleach.clean('Vegan Friendly, Plant-Protein Smart, Fiber Smart, Low Glycemic, Gluten-Free, Dairy-Free', strip=True))

        if not MealPlan.query.first():
            db.session.add_all([meal1, meal2, meal3, meal4, meal5, meal6, meal7, meal8, meal9])
            db.session.commit()
        
        testimoni1 = Testimonial(Name=bleach.clean('Andini Kusuma', strip=True), Rating=5, ReviewMessage=bleach.clean("I've been using SEA Catering for three months and I feel healthier, more energetic, and my weight is finally under control. The meals are always fresh and tasty. I love how they personalize everything to my needs!", strip=True))
        testimoni2 = Testimonial(Name=bleach.clean('Michael Santoso', strip=True), Rating=4, ReviewMessage=bleach.clean("SEA Catering makes my busy life so much easier. I no longer have to worry about planning meals. I especially appreciate the balanced nutrition and how they cater to my dietary restrictions.", strip=True))
        testimoni3 = Testimonial(Name=bleach.clean('Rina Halim', strip=True), Rating=5, ReviewMessage=bleach.clean("Delicious, clean, and convenient! As a mom with two kids, I really value the time SEA Catering saves me. Their customer service is also super responsive. Highly recommended!", strip=True))
        testimoni4 = Testimonial(Name=bleach.clean('Yoga Pratama', strip=True), Rating=4, ReviewMessage=bleach.clean("I’m training for a triathlon, and SEA Catering has helped me stay on track with my meal prep. Portion control and macros are just right. Just wish they had a few more spicy options.", strip=True))
        testimoni5 = Testimonial(Name=bleach.clean('Clarissa Gunawan', strip=True), Rating=5, ReviewMessage=bleach.clean("The best meal service I’ve ever tried! Every dish tastes home-cooked, and I love how they adapt to my health goals. Even my doctor noticed improvements in my blood sugar and cholesterol levels.", strip=True))

        if not Testimonial.query.first():
            db.session.add_all([testimoni1, testimoni2, testimoni3, testimoni4, testimoni5])
            db.session.commit()
        
        admin1 = User(Email=bleach.clean('lucia@gmail.com', strip=True), Name=bleach.clean('Lucia', strip=True), Password=bcrypt.generate_password_hash(bleach.clean('asdfghjkl', strip=True)).decode('utf-8'), Role=bleach.clean('admin', strip=True))
        admin2 = User(Email=bleach.clean('giovani@gmail.com', strip=True), Name=bleach.clean('Giovani', strip=True), Password=bcrypt.generate_password_hash(bleach.clean('zxcvbnm', strip=True)).decode('utf-8'), Role=bleach.clean('admin', strip=True))

        if not User.query.first():
            db.session.add_all([admin1, admin2])
            db.session.commit()

        db.session.close()

    app.run(debug=True)
    app.run(host='0.0.0.0', port=10000)
