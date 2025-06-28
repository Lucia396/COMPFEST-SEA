from datetime import datetime, timedelta
from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

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
    SubscriptionTime = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"Subscription('{self.SubscriptionID}', '{self.Name}')"
    
class Modify(db.Model):
    __tablename__ = 'Modify'
    ModifyID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    SubscriptionID = db.Column(db.Integer, db.ForeignKey('Subscription.SubscriptionID'), nullable=False)
    Time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    Status = db.Column(db.String(32), nullable=False)
    Subscription = db.relationship('Subscription', backref='subsid', lazy=True)

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
    if request.method == 'GET':
        testimonial = Testimonial.query.all()
        return render_template("home.html", testimonial=testimonial)
    
    if 'email' in session and session['role'] == 'user':
        name = request.form.get('Name')
        rating = request.form.get('Rating')
        review = request.form.get('Review Message')

        if name != User.query.filter_by(Email=session['email']).first().Name:
            flash('Please input the same name as profile username!')
            return render_template("home.html")
        
        testimoni = Testimonial(Name=name, Rating=rating, ReviewMessage=review)
        db.session.add(testimoni)
        db.session.commit()

        flash('Thank you for your testimonial!')
        return render_template("home.html")
    
    return render_template("home.html")

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if 'email' in session:
        flash('You are already logged in!')
        return redirect(url_for('home'))

    if request.method == 'GET':
        return render_template("login.html")
    
    email = request.form.get('Email')
    password = request.form.get('Password')
    user = User.query.filter_by(Email=email).first()

    if not user or not bcrypt.check_password_hash(user.Password, password):
        flash('Please check your login details and try again!')
        return render_template('login.html')
    
    session['email'] = email
    session['role'] = user.Role
    session.permanent = True
    return redirect(url_for('home'))

@app.route('/register', methods = ['POST', 'GET'])
def register():
    if 'email' in session:
        flash('You are already logged in!')
        return redirect(url_for('home'))
    
    if request.method == 'GET':
        return render_template("register.html")
    
    name = request.form.get('Name')
    email = request.form.get('Email')
    password = bcrypt.generate_password_hash(request.form.get('Password')).decode('utf-8')

    if User.query.filter_by(Email=email).first():
        flash('Email has been used. Try other email!')
        return render_template('register.html')
    
    user = User(Email=email, Name=name, Password=password, Role='user')
    db.session.add(user)
    db.session.commit()

    flash('Your data has been added. Please Login!')
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
        
            name = request.form.get('Name')
            phone = request.form.get('Phone Number')
            plan = request.form.get('Plan')
            types = request.form.getlist('Time')
            days = request.form.getlist('Day')
            allergies = request.form.get('Allergies')
            status = 'active'

            if name != User.query.filter_by(Email=session['email']).first().Name:
                flash('Please input the same name as profile username!')
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

            flash('You have successfully subscribe a new meal plan!')
            return redirect(url_for('home'))
        
        flash('You are an admin. Please login as a user to subscribe!')
        return redirect(url_for('home'))
    
    flash('Please login before subscribing!')
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
    
    flash('Please login to access your account!')
    return redirect(url_for('login')) 

@app.route('/view-subscription')
def viewSubscription():
    if 'email' in session:
        if session['role'] == 'user':
            name = User.query.filter_by(Email=session['email']).first().Name
            subscriptions = Subscription.query.filter_by(Name=name).all()

            if not subscriptions:
                flash('There is no subscription have been made. Please subscribe to see your subscription!') 
                return redirect(url_for('subscription'))

            for subscription in subscriptions:
                if subscription.Status == 'active':
                    return render_template("view-subscription.html", subscriptions=subscriptions)
            flash('All of your subscriptions are inactive. Please Reactivate to see your subscription!') 
            return redirect(url_for('dashboard'))
        
        flash('You are an admin. Please login as a user to subscribe!')
        return redirect(url_for('dashboard'))
    
    flash('Please login before subscribing!')
    return redirect(url_for('login'))

@app.route('/pause-subscription')
def pausesubscription():
    if 'email' in session:
        if session['role'] == 'user':
            name = User.query.filter_by(Email=session['email']).first().Name
            subscriptions = Subscription.query.filter_by(Name=name).all()

            if not subscriptions:
                flash('There is no subscription have been made. Please subscribe to manage your subscription!') 
                return redirect(url_for('subscription'))

            for subscription in subscriptions:
                if subscription.Status == 'active':
                    return render_template("pause-subscription.html", subscriptions=subscriptions)
            
            flash('All of your subscriptions are inactive. Please Reactivate to manage your subscription!') 
            return redirect(url_for('dashboard'))
        
        flash('You are an admin. Please login as a user to subscribe!')
        return redirect(url_for('dashboard'))
    
    flash('Please login before subscribing!')
    return redirect(url_for('login'))

@app.route('/pause-subscription/<int:SubscriptionID>', methods=['POST'])
def pauseSubscription(SubscriptionID):
    if 'email' in session:
        if session['role'] == 'user':
            subscription = Subscription.query.get_or_404(SubscriptionID)
            subscription.Status = 'inactive'
            modification = Modify(SubscriptionID=SubscriptionID, Status='pause')
            db.session.add(modification)
            db.session.commit()
            
            flash('You have successfully pause your subscription!')
            return redirect(url_for('dashboard'))

        flash('You are an admin. Please login as a user to subscribe!')
        return redirect(url_for('dashboard'))
    
    flash('Please login before subscribing!')
    return redirect(url_for('login'))

@app.route('/reactivate-subscription')
def reactivatesubscription():
    if 'email' in session:
        if session['role'] == 'user':
            name = User.query.filter_by(Email=session['email']).first().Name
            subscriptions = Subscription.query.filter_by(Name=name).all()

            if not subscriptions:
                flash('There is no subscription have been made. Please subscribe to manage your subscription!') 
                return redirect(url_for('subscription'))

            for subscription in subscriptions:
                if subscription.Status == 'inactive':
                    return render_template("reactivate-subscription.html", subscriptions=subscriptions)
            
            flash('All of your subscriptions are active!') 
            return redirect(url_for('dashboard'))
        
        flash('You are an admin. Please login as a user to subscribe!')
        return redirect(url_for('dashboard'))
    
    flash('Please login before subscribing!')
    return redirect(url_for('login'))

@app.route('/reactivate-subscription/<int:SubscriptionID>', methods=['POST'])
def reactivateSubscription(SubscriptionID):
    if 'email' in session:
        if session['role'] == 'user':
            subscription = Subscription.query.get_or_404(SubscriptionID)
            subscription.Status = 'active'
            modification = Modify(SubscriptionID=SubscriptionID, Status='reactivate')
            db.session.add(modification)
            db.session.commit()
            
            flash('You have successfully reactivate your subscription!')
            return redirect(url_for('dashboard'))

        flash('You are an admin. Please login as a user to subscribe!')
        return redirect(url_for('dashboard'))
    
    flash('Please login before subscribing!')
    return redirect(url_for('login'))

@app.route('/cancel-subscription')
def cancelsubscription():
    if 'email' in session:
        if session['role'] == 'user':
            name = User.query.filter_by(Email=session['email']).first().Name
            subscriptions = Subscription.query.filter_by(Name=name).all()

            if not subscriptions:
                flash('There is no subscription have been made. Please subscribe to manage your subscription!') 
                return redirect(url_for('subscription'))

            return render_template("cancel-subscription.html", subscriptions=subscriptions)
        
        flash('You are an admin. Please login as a user to subscribe!')
        return redirect(url_for('dashboard'))
    
    flash('Please login before subscribing!')
    return redirect(url_for('login'))

@app.route('/cancel-subscription/<int:SubscriptionID>', methods=['POST'])
def cancelSubscription(SubscriptionID):
    if 'email' in session:
        if session['role'] == 'user':
            subscription = Subscription.query.get_or_404(SubscriptionID)
            db.session.delete(subscription)
            db.session.commit()
            
            flash('You have successfully cancel your subscription!')
            return redirect(url_for('dashboard'))

        flash('You are an admin. Please login as a user to subscribe!')
        return redirect(url_for('dashboard'))
    
    flash('Please login before subscribing!')
    return redirect(url_for('login'))

@app.route('/new-subscriptions', methods=['POST', 'GET'])
def newSubscriptions():
    subscriptions = None
    if 'email' in session:
        if session['role'] == 'admin':
            if request.method == 'POST':
                start = datetime.strptime(request.form.get('start_date'), "%Y-%m-%dT%H:%M")
                end = datetime.strptime(request.form.get('end_date'), "%Y-%m-%dT%H:%M")

                if start > end:
                    flash('The date is not valid!')
                    return redirect(url_for('newSubscriptions'))
                
                subscriptions = Subscription.query.filter(Subscription.SubscriptionTime.between(start, end)).all()
                if not subscriptions:
                    flash('There is no subscription in selected date!')
                    return redirect(url_for('dashboard'))
                
            return render_template("new-subscriptions.html", subscriptions=subscriptions)
        
        flash('You are a user. Please login as an admin to access!')
        return redirect(url_for('dashboard'))
    
    flash('Please login before accesssing!')
    return redirect(url_for('login'))

@app.route('/monthly-recurring-revenue', methods=['POST', 'GET'])
def monthlyRecurringRevenue():
    amount = None
    subscriptions = None
    if 'email' in session:
        if session['role'] == 'admin':
            if request.method == 'POST':
                start = datetime.strptime(request.form.get('start_date'), "%Y-%m-%dT%H:%M")
                end = datetime.strptime(request.form.get('end_date'), "%Y-%m-%dT%H:%M")

                if start > end:
                    flash('The date is not valid!')
                    return redirect(url_for('monthlyRecurringRevenue'))
                
                subscriptions = Subscription.query.filter(Subscription.SubscriptionTime.between(start, end)).all()
                if not subscriptions:
                    flash('There is no subscription in selected date!')
                    return redirect(url_for('dashboard'))
                
                amount = 0
                for subscription in subscriptions:
                    amount += subscription.Prices
                
            return render_template("monthly-recurring-revenue.html", subscriptions=subscriptions, amount=amount)
        
        flash('You are a user. Please login as an admin to access!')
        return redirect(url_for('dashboard'))
    
    flash('Please login before accesssing!')
    return redirect(url_for('login'))

@app.route('/reactivations', methods=['POST', 'GET'])
def reactivations():
    subscriptions = None
    if 'email' in session:
        if session['role'] == 'admin':
            if request.method == 'POST':
                start = datetime.strptime(request.form.get('start_date'), "%Y-%m-%dT%H:%M")
                end = datetime.strptime(request.form.get('end_date'), "%Y-%m-%dT%H:%M")

                if start > end:
                    flash('The date is not valid!')
                    return redirect(url_for('reactivations'))

                items = Modify.query.filter(Modify.Time.between(start, end)).all()
                if not items:
                    flash('There is no subscription in selected date!')
                    return redirect(url_for('dashboard'))
                
                pause = []
                for item in items:
                    if item.Status == 'pause':
                        pause.append(item)
                
                subscriptions = []
                for subs in pause:
                    items = Modify.query.filter(Modify.Time.between(subs.Time, end)).all()
                    for item in items:
                        if item.Status == 'reactivate' and item.SubscriptionID == subs.SubscriptionID:
                            subscription = Subscription.query.filter_by(SubscriptionID=item.SubscriptionID).first()
                            subscriptions.append(subscription)
            
            return render_template("reactivations.html", subscriptions=subscriptions)
        
        flash('You are a user. Please login as an admin to access!')
        return redirect(url_for('dashboard'))
    
    flash('Please login before accesssing!')
    return redirect(url_for('login'))

@app.route('/subscription-growth')
def subscriptionGrowth():
    if 'email' in session:
        if session['role'] == 'admin':
            subscriptions = Subscription.query.filter_by(Status='active').all()
            if not subscriptions:
                flash('There is no active subscription!') 
                return redirect(url_for('dashboard'))
            return render_template("subscription-growth.html", subscriptions=subscriptions)
        
        flash('You are a user. Please login as an admin to access!')
        return redirect(url_for('dashboard'))
    
    flash('Please login before accesssing!')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('email', default=None)
    session.pop('role', default=None)
    flash('You were logged out!')
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
        meal1 = MealPlan(MealPlanName='Grilled Chicken Quinoa Bowl', ShortDes='with Roasted Bell Peppers, Broccoli, and Honey-Lime Dressing', Price='Rp 47.000,00', Description=des1, NutritionalInfo=nutri1, Allergens='None', Tags='Protein Smart, Calorie Smart, Fiber Smart, Low Sugar, Gluten-Free, Dairy-Free')
        
        des2 = '''Flavor-rich Japanese-inspired dish designed for those seeking a well-balanced and protein-dense meal. 
            Featuring a thick fillet of Atlantic salmon, delicately grilled and glazed with a homemade light teriyaki sauce made from low-sodium soy, garlic, and a touch of honey.
            Served with a side of steamed brown rice and a colorful medley of stir-fried vegetables—carrots, bok choy, and shiitake mushrooms—this bento box offers a rich umami experience without excess sodium or sugar.
            The bento is finished with a sprinkle of sesame seeds and chopped scallions for a fresh, aromatic finish.'''
        nutri2 = '''Serving Size - 450 gram. 🔥 Calories - 480 kcal. 🥩 Protein - 32 gram. 🍚 Carbohydrates - 40 gram. 🍯 Sugars - 8 gram. 🥑 Fat - 18 gram. 🥬 Fiber - 5 gram. 🧂 Sodium - 520 miligram. 🍊 Vitamins - rich in Vitamin A, B12, C, and D'''
        meal2 = MealPlan(MealPlanName='Salmon Teriyaki Bento', ShortDes='Salmon Teriyaki-Glazed, with Brown Rice and Stir-Fried Vegetables', Price='Rp 65.000,00', Description=des2, NutritionalInfo=nutri2, Allergens='Soy, Fish, Sesame, Gluten', Tags='Protein Smart, Omega-3 Rich, Fiber Smart, Low Sugar, Dairy-Free')
        
        des3 = '''A plant-powered, high-protein bowl designed for clean energy and vibrant nutrition, features firm tofu cubes, pan-seared to golden perfection and tossed in a garlic-ginger soy sauce glaze, delivering that savory umami punch without overpowering saltiness.
            Accompanied by a colorful medley of seasonal vegetables like bok choy, carrots, red bell peppers, and snap peas, all stir-fried lightly in sesame oil to preserve their crunch and nutrients.
            Served over a small bed of red rice or brown rice, this bowl is light, filling, and completely plant-based.
            Ideal for anyone seeking a vegan, high-protein, fiber-rich, and low-cholesterol meal option.'''
        nutri3 = '''Serving Size - 400 gram. 🔥 Calories - 370 kcal. 🥩 Protein - 22 gram. 🍚 Carbohydrates - 33 gram. 🍯 Sugars - 6 gram. 🥑 Fat - 15 gram. 🥬 Fiber - 7 gram. 🧂 Sodium - 469 miligram. 🍊 Vitamins - rich in Vitamin A, B1, C, and K'''
        meal3 = MealPlan(MealPlanName='Tofu Veggie Stir Fry', ShortDes='Tofu with Sautéed Vegetables and Garlic-Ginger Sauce', Price='Rp 34.000,00', Description=des3, NutritionalInfo=nutri3, Allergens='Soy, Sesame, Gluten', Tags='Protein Smart, Vegan Friendly, Fiber Smart, Low Glycemic, Dairy-Free')
        
        des4 = '''This meal features slices of marinated tempeh, grilled until golden and slightly crisp on the edges, seasoned with a blend of Mediterranean herbs like thyme, rosemary, and oregano.
                The tempeh is layered with crisp lettuce, sliced tomatoes, cucumber, and a spoonful of house-made herbed yogurt sauce, all wrapped inside a whole wheat tortilla.
                The sauce adds a creamy tang with fresh mint and lemon undertones, making this wrap a nutrient-packed option perfect for lunch or a light dinner.'''
        nutri4 = '''Serving Size - 350 gram. 🔥 Calories - 400 kcal. 🥩 Protein - 25 gram. 🍚 Carbohydrates - 35 gram. 🍯 Sugars - 5 gram. 🥑 Fat - 13 gram. 🥬 Fiber - 6 gram. 🧂 Sodium - 420 miligram. 🍊 Vitamins - rich in Vitamin A, B1, C, and K'''
        meal4 = MealPlan(MealPlanName='Herbed Grilled Tempeh Wrap', ShortDes='Grilled Tempeh Wrapped with Lettuce, Tomato, and Herbed Yogurt in Whole Wheat Wrap', Price='Rp 36.000,00', Description=des4, NutritionalInfo=nutri4, Allergens='Soy, Dairy, Gluten', Tags='Protein Smart, Vegetarian, Fiber Smart')
        
        des5 = '''This box features grilled chicken satay skewers, marinated in aromatic spices and herbs, then grilled over an open flame for charred edges and juicy tenderness.
                It's paired with a lightly sweet and spicy peanut sauce, made with natural peanut butter, coconut milk, garlic, and chili.
                On the side: a refreshing cucumber and red onion salad with a touch of lime for acidity, and a creamy, nutrient-dense sweet potato mash, lightly seasoned with olive oil and sea salt.
                This meal is designed to fuel your day with lean protein, complex carbs, and healthy fats — perfect for gym-goers or those seeking sustained energy.'''
        nutri5 = '''Serving Size - 420 gram. 🔥 Calories - 510 kcal. 🥩 Protein - 35 gram. 🍚 Carbohydrates - 28 gram. 🍯 Sugars - 6 gram. 🥑 Fat - 22 gram. 🥬 Fiber - 5 gram. 🧂 Sodium - 540 miligram. 🍊 Vitamins - rich in Vitamin A, B1, C, and E'''
        meal5 = MealPlan(MealPlanName='Chicken Satay Protein Box', ShortDes='Grilled Chicken Skewers with Peanut Sauce, Cucumber Salad, and Sweet Potato Mash', Price='Rp 42.000,00', Description=des5, NutritionalInfo=nutri5, Allergens='Soy, Peanut, Gluten', Tags='Protein Smart, Calorie Smart, Fiber Smart, Low Sugar')
        
        des6 = '''A deeply flavorful and aromatic Indonesian classic, Pepes Ikan features fresh white fish (typically mackerel or snapper) marinated in a rich blend of traditional spices-turmeric, lemongrass, garlic, chili, and kaffir lime leaves.
                The fish is then wrapped in banana leaves and steamed or grilled, allowing the spices to infuse while keeping the dish moist and oil-free.
                It's served with a portion of red rice, known for its higher fiber and lower glycemic index compared to white rice, and a side of blanched lemon basil (kemangi) or sautéed vegetables.'''
        nutri6 = '''Serving Size - 400 gram. 🔥 Calories - 430 kcal. 🥩 Protein - 34 gram. 🍚 Carbohydrates - 38 gram. 🍯 Sugars - 3 gram. 🥑 Fat - 12 gram. 🥬 Fiber - 5 gram. 🧂 Sodium - 450 miligram. 🍊 Vitamins - rich in Vitamin A, B12, C, and D'''
        meal6 = MealPlan(MealPlanName='Pepes Ikan', ShortDes='Steamed Spiced Mackerel in Banana Leaf with Red Rice and Lemon Basil', Price='Rp 37.000,00', Description=des6, NutritionalInfo=nutri6, Allergens='Fish', Tags='Protein Smart, Fiber Smart, Gluten-Free, Dairy-Free')
        
        des7 = '''This bold and aromatic dish hails from Manado, North Sulawesi, and features chicken simmered in a vibrant yellow spice blend known as woku.
                Made from turmeric, chili, lemongrass, and lime leaves, ayam woku is fragrant, slightly spicy, and full of herbal depth.
                It's served with red rice (nasi merah) for added fiber and minerals, and accompanied by a side of sautéed leafy greens such as water spinach (kangkung) or cassava leaves (daun singkong), lightly cooked with garlic.'''
        nutri7 = '''Serving Size - 420 gram. 🔥 Calories - 460 kcal. 🥩 Protein - 36 gram. 🍚 Carbohydrates - 38 gram. 🍯 Sugars - 4 gram. 🥑 Fat - 14 gram. 🥬 Fiber - 5 gram. 🧂 Sodium - 510 miligram. 🍊 Vitamins - rich in Vitamin A, B6, and C'''
        meal7 = MealPlan(MealPlanName='Woku Chicken', ShortDes='Spicy Manado-style Chicken Stew with Red Rice and Sautéed Water Spinach', Price='Rp 45.000,00', Description=des7, NutritionalInfo=nutri7, Allergens='None', Tags='Protein Smart, Fiber Smart, Gluten-Free, Dairy-Free')
        
        des8 = '''A light, comforting, and immune-boosting dish made with free-range chicken (ayam kampung) simmered slowly in a clear broth with carrots, potatoes, young corn, celery, and shallots.
                Unlike creamy or heavy soups, it is all about clarity and purity—flavored with simple aromatics like white pepper, garlic, and a touch of nutmeg.
                Served warm with a side of red rice or as a standalone soup, it's ideal for a low-calorie, hydrating meal, commonly enjoyed across Indonesia as a healthy home remedy or post-illness comfort food.'''
        nutri8 = '''Serving Size - 400 gram. 🔥 Calories - 310 kcal. 🥩 Protein - 26 gram. 🍚 Carbohydrates - 22 gram. 🍯 Sugars - 3 gram. 🥑 Fat - 9 gram. 🥬 Fiber - 4 gram. 🧂 Sodium - 420 miligram. 🍊 Vitamins - rich in Vitamin A, B6, C, and K'''
        meal8 = MealPlan(MealPlanName='Clear Chicken Soup', ShortDes='Clear Chicken and Vegetable Soup with Young Corn, Carrots, and Celery', Price='Rp 50.000,00', Description=des8, NutritionalInfo=nutri8, Allergens='None', Tags='Low Calorie, Immune Boosting, Gluten-Free, Dairy-Free')

        des9 = '''A wholesome and vibrant plant-based Indonesian classic, it consists of a generous medley of lightly steamed vegetables—such as spinach, long beans, bean sprouts, and cabbage—tossed with urap, a traditional mixture of grated coconut, garlic, kaffir lime leaves, and chili.
                Served alongside grilled tempeh marinated in a sweet-savory glaze, this meal is packed with fiber, plant protein, and rich Indonesian flavors.
                It's perfect for vegetarians, vegans, or anyone looking for a deeply satisfying yet clean and nutritious local option.'''
        nutri9 = '''Serving Size - 400 gram. 🔥 Calories - 390 kcal. 🥩 Protein - 21 gram. 🍚 Carbohydrates - 28 gram. 🍯 Sugars - 6 gram. 🥑 Fat - 18 gram. 🥬 Fiber - 8 gram. 🧂 Sodium - 440 miligram. 🍊 Vitamins - rich in Vitamin A, C, and K'''
        meal9 = MealPlan(MealPlanName='Urap Sayur with Tempe Bakar', ShortDes='Steamed Vegetables with Seasoned Grated Coconut, paired with Grilled Tempeh', Price='Rp 33.000,00', Description=des9, NutritionalInfo=nutri9, Allergens='Soy, Coconut', Tags='Vegan Friendly, Plant-Protein Smart, Fiber Smart, Low Glycemic, Gluten-Free, Dairy-Free')

        if not MealPlan.query.first():
            db.session.add_all([meal1, meal2, meal3, meal4, meal5, meal6, meal7, meal8, meal9])
            db.session.commit()
        
        testimoni1 = Testimonial(Name='Andini Kusuma', Rating=5, ReviewMessage="I've been using SEA Catering for three months and I feel healthier, more energetic, and my weight is finally under control. The meals are always fresh and tasty. I love how they personalize everything to my needs!")
        testimoni2 = Testimonial(Name='Michael Santoso', Rating=4, ReviewMessage="SEA Catering makes my busy life so much easier. I no longer have to worry about planning meals. I especially appreciate the balanced nutrition and how they cater to my dietary restrictions.")
        testimoni3 = Testimonial(Name='Rina Halim', Rating=5, ReviewMessage="Delicious, clean, and convenient! As a mom with two kids, I really value the time SEA Catering saves me. Their customer service is also super responsive. Highly recommended!")
        testimoni4 = Testimonial(Name='Yoga Pratama', Rating=4, ReviewMessage="I’m training for a triathlon, and SEA Catering has helped me stay on track with my meal prep. Portion control and macros are just right. Just wish they had a few more spicy options.")
        testimoni5 = Testimonial(Name='Clarissa Gunawan', Rating=5, ReviewMessage="The best meal service I’ve ever tried! Every dish tastes home-cooked, and I love how they adapt to my health goals. Even my doctor noticed improvements in my blood sugar and cholesterol levels.")

        if not Testimonial.query.first():
            db.session.add_all([testimoni1, testimoni2, testimoni3, testimoni4, testimoni5])
            db.session.commit()
        
        admin1 = User(Email='lucia@gmail.com', Name='Lucia', Password=bcrypt.generate_password_hash('asdfghjkl').decode('utf-8'), Role='admin')
        admin2 = User(Email='giovani@gmail.com', Name='Giovani', Password=bcrypt.generate_password_hash('zxcvbnm').decode('utf-8'), Role='admin')

        if not User.query.first():
            db.session.add_all([admin1, admin2])
            db.session.commit()

        db.session.close()

    app.run(debug=True)
