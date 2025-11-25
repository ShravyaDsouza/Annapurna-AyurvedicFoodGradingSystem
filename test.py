from flask import Flask, render_template, request, redirect, url_for, flash ,session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'ee541147b2d6c0f9c00de2090d566fe3e4ef1d816bdb8aa5c5100be7a1300a01'

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/annapurna"
mongo = PyMongo(app)
client = MongoClient('mongodb://localhost:27017/')
db = client.annapurna
collection = db.articles

# Load the Excel file for ingredient grading
file_path = '/Users/shravyadsouza/Desktop/MIT/DE-minipro-ingredients.xlsx'
df = pd.read_excel(file_path)

# Home (Landing Page) - Display Articles
@app.route('/')
def landing():
    articles = collection.find({}, {"title": 1, "content": 1})  # Fetching article titles and content
    return render_template('landing.html', articles=articles)

# Signup page
@app.route('/signup')
def signup():
    return render_template('signup.html')

# Handle Signup form submission
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['mail']
        phone_number = request.form['phoneno']
        password = request.form['password']
        repeat_password = request.form['rpassword']
        age = request.form['age']
        blood_group = request.form['bloodgroup']
        gender = request.form['gender']
        dosha = request.form['dosha']

        # Check if passwords match
        if password != repeat_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('signup'))

        # Check if the user already exists
        if mongo.db.users.find_one({"email": email}):
            flash('User already exists', 'error')
            return redirect(url_for('signup'))

        # Hash the password for security
        hashed_password = generate_password_hash(password)

        # Insert new user into the database
        try:
            mongo.db.users.insert_one({
                'name': name,
                'email': email,
                'phone_number': phone_number,
                'password': hashed_password,
                'age': age,
                'blood_group': blood_group,
                'gender': gender,
                'dosha': dosha
            })
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('signin'))
        except Exception as e:
            flash(f'An error occurred while registering: {str(e)}', 'error')
            return redirect(url_for('signup'))

# Signin page
@app.route('/signin')
def signin():
    return render_template('signin.html')

# Handle Signin form submission
@app.route('/login', methods=['POST'])
def login():
    email = request.form['mail']
    password = request.form['password']

    # Check if the user exists in the database
    user = mongo.db.users.find_one({"email": email})

    if user:
        # Check if the provided password matches the hashed password in the database
        if check_password_hash(user['password'], password):
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid password', 'error')
            return redirect(url_for('signin'))
    else:
        flash('User does not exist', 'error')
        return redirect(url_for('signin'))

# Example dashboard route (after successful login)
@app.route('/dashboard')from flask import Flask, render_template, request, redirect, url_for, flash ,session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'ee541147b2d6c0f9c00de2090d566fe3e4ef1d816bdb8aa5c5100be7a1300a01'

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/annapurna"
mongo = PyMongo(app)
client = MongoClient('mongodb://localhost:27017/')
db = client.annapurna
collection = db.articles

# Load the Excel file for ingredient grading
file_path = '/Users/shravyadsouza/Desktop/MIT/DE-minipro-ingredients.xlsx'
df = pd.read_excel(file_path)

# Home (Landing Page) - Display Articles
@app.route('/')
def landing():
    articles = collection.find({}, {"title": 1, "content": 1})  # Fetching article titles and content
    return render_template('landing.html', articles=articles)

# Signup page
@app.route('/signup')
def signup():
    return render_template('signup.html')

# Handle Signup form submission
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['mail']
        phone_number = request.form['phoneno']
        password = request.form['password']
        repeat_password = request.form['rpassword']
        age = request.form['age']
        blood_group = request.form['bloodgroup']
        gender = request.form['gender']
        dosha = request.form['dosha']

        # Check if passwords match
        if password != repeat_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('signup'))

        # Check if the user already exists
        if mongo.db.users.find_one({"email": email}):
            flash('User already exists', 'error')
            return redirect(url_for('signup'))

        # Hash the password for security
        hashed_password = generate_password_hash(password)

        # Insert new user into the database
        try:
            mongo.db.users.insert_one({
                'name': name,
                'email': email,
                'phone_number': phone_number,
                'password': hashed_password,
                'age': age,
                'blood_group': blood_group,
                'gender': gender,
                'dosha': dosha
            })
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('signin'))
        except Exception as e:
            flash(f'An error occurred while registering: {str(e)}', 'error')
            return redirect(url_for('signup'))

# Signin page
@app.route('/signin')
def signin():
    return render_template('signin.html')

# Handle Signin form submission
@app.route('/login', methods=['POST'])
def login():
    email = request.form['mail']
    password = request.form['password']

    # Check if the user exists in the database
    user = mongo.db.users.find_one({"email": email})

    if user:
        # Check if the provided password matches the hashed password in the database
        if check_password_hash(user['password'], password):
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid password', 'error')
            return redirect(url_for('signin'))
    else:
        flash('User does not exist', 'error')
        return redirect(url_for('signin'))

# Example dashboard route (after successful login)
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Route to display an individual article
@app.route('/article/<article_id>')
def article(article_id):
    try:
        # Find the article by its ObjectId
        article = collection.find_one({"_id": ObjectId(article_id)})

        if article:
            return render_template('article.html', article=article)
        else:
            return "Article not found", 404
    except Exception as e:
        return f"Invalid article ID: {e}", 400

# Step 1: Category Selection
@app.route('/grading/categories', methods=['GET', 'POST'])
def select_categories():
    if request.method == 'POST':
        selected_categories = request.form.getlist('categories')
        if not selected_categories:
            flash('Please select at least one category', 'error')
            return redirect(url_for('select_categories'))
        session['categories'] = selected_categories  # Store categories in session
        return redirect(url_for('enter_ingredients'))

    categories = get_categories()
    return render_template('/partials/categories.html', categories=categories)


# Step 2: Enter Ingredients for Selected Categories
@app.route('/grading/ingredients', methods=['GET', 'POST'])
def enter_ingredients():
    selected_categories = session.get('categories', [])
    if not selected_categories:
        return redirect(url_for('select_categories'))  # Redirect if no categories

    if request.method == 'POST':
        ingredients = {category: request.form.get(category) for category in selected_categories}
        session['ingredients'] = ingredients  # Store ingredients in session
        return redirect(url_for('select_dosha'))

    return render_template('partials/ingredient_form.html', categories=selected_categories)


# Step 3: Dosha Selection
@app.route('/grading/dosha', methods=['GET', 'POST'])
def select_dosha():
    if request.method == 'POST':
        dosha = request.form['dosha']
        session['dosha'] = dosha  # Store dosha in session
        return redirect(url_for('grading_results'))

    return render_template('partials/dosha_form.html')


# Step 4: Display Results
@app.route('/grading/results')
def grading_results():
    categories = session.get('categories', [])
    ingredients = session.get('ingredients', {})
    dosha = session.get('dosha', '')

    # Ensure required data is available
    if not categories or not ingredients or not dosha:
        return redirect(url_for('select_categories'))

    # Perform grading logic
    results = []
    grade = 0
    total_ingredients = len(ingredients)

    for category, ingredient in ingredients.items():
        alternatives = get_alternative_ingredients(df, dosha, category, ingredient)
        if isinstance(alternatives, str):
            results.append(alternatives)
            grade += 1
        elif isinstance(alternatives, list) and alternatives:
            for alt in alternatives:
                results.append(f"Ingredient: {alt['Ingredient']}, Restricted Form: {alt['Restricted Form']}, Preferred Form: {alt['Preferred Form']}")
        else:
            results.append(f"No alternatives found for {ingredient} in {category}.")

    # Calculate final grade
    scaled_grade = (grade / total_ingredients) * 5 if total_ingredients > 0 else 0
    timestamp = datetime.now()

    # Fetch the logged-in user's email
    user_email = session.get('email')

    # Store the grading results in MongoDB
    try:
        mongo.db.users.update_one(
            {"email": user_email},
            {"$push": {
                "grading_results": {
                    "categories": categories,
                    "ingredients": ingredients,
                    "dosha": dosha,
                    "results": results,  # Store the results
                    "grade": scaled_grade,
                    "timestamp": timestamp
                }
            }}
        )
        flash('Grading results saved successfully!', 'success')
        return redirect(url_for('dashboard'))  # Redirect to the dashboard or another page
    except Exception as e:
        flash(f'Error storing grading results: {str(e)}', 'error')
        return redirect(url_for('select_categories'))


def get_alternative_ingredients(df, dosh, category, ingredient):
    if category not in df.columns or dosh.capitalize() not in df.columns:
        raise ValueError(f"Invalid category '{category}' or dosh '{dosh}'.")

    ingredient = ingredient.lower()
    match = df[(df[category] == 1) & (df[dosh.capitalize()] == 1)]

    if ingredient in match['Ingredient'].str.lower().values:
        restricted_info = \
        match[match['Ingredient'].str.lower() == ingredient][['Restricted Form', 'Preferred Form']].iloc[0]
        return f"The ingredient '{ingredient}' is already suitable. <br>Restricted: {restricted_info['Restricted Form']} <br>Preferred: {restricted_info['Preferred Form']}"

    alternatives = df[(df[dosh.capitalize()] == 1) & (df[category] == 1)]
    unique_alternatives = alternatives[~alternatives['Ingredient'].str.lower().duplicated()]

    result = []
    for _, row in unique_alternatives.iterrows():
        result.append({
            'Ingredient': row['Ingredient'],
            'Restricted Form': row['Restricted Form'],
            'Preferred Form': row['Preferred Form']
        })
        if len(result) >= 3:
            break

    return result

def get_categories():
    # Assuming df is your DataFrame loaded from the CSV/Excel file
    # Exclude non-category columns like 'Ingredient', 'Restricted Form', etc.
    excluded_columns = ['Ingredient', 'Restricted Form', 'Preferred Form', 'Vatta', 'Pitta', 'Kapha','Frequency']
    categories = [col for col in df.columns if col not in excluded_columns]
    return categories

@app.route('/grading/categories', methods=['GET'])
def get_categories_route():
    categories = get_categories()
    return render_template('partials/categories.html', categories=categories)

# About and other pages
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)

def dashboard():
    return render_template('dashboard.html')

# Route to display an individual article
@app.route('/article/<article_id>')
def article(article_id):
    try:
        # Find the article by its ObjectId
        article = collection.find_one({"_id": ObjectId(article_id)})

        if article:
            return render_template('article.html', article=article)
        else:
            return "Article not found", 404
    except Exception as e:
        return f"Invalid article ID: {e}", 400

# Step 1: Category Selection
@app.route('/grading/categories', methods=['GET', 'POST'])
def select_categories():
    if request.method == 'POST':
        selected_categories = request.form.getlist('categories')
        if not selected_categories:
            flash('Please select at least one category', 'error')
            return redirect(url_for('select_categories'))
        session['categories'] = selected_categories  # Store categories in session
        return redirect(url_for('enter_ingredients'))

    categories = get_categories()
    return render_template('/partials/categories.html', categories=categories)


# Step 2: Enter Ingredients for Selected Categories
@app.route('/grading/ingredients', methods=['GET', 'POST'])
def enter_ingredients():
    selected_categories = session.get('categories', [])
    if not selected_categories:
        return redirect(url_for('select_categories'))  # Redirect if no categories

    if request.method == 'POST':
        ingredients = {category: request.form.get(category) for category in selected_categories}
        session['ingredients'] = ingredients  # Store ingredients in session
        return redirect(url_for('select_dosha'))

    return render_template('partials/ingredient_form.html', categories=selected_categories)


# Step 3: Dosha Selection
@app.route('/grading/dosha', methods=['GET', 'POST'])
def select_dosha():
    if request.method == 'POST':
        dosha = request.form['dosha']
        session['dosha'] = dosha  # Store dosha in session
        return redirect(url_for('grading_results'))

    return render_template('partials/dosha_form.html')


# Step 4: Display Results
@app.route('/grading/results')
def grading_results():
    categories = session.get('categories', [])
    ingredients = session.get('ingredients', {})
    dosha = session.get('dosha', '')

    # Ensure required data is available
    if not categories or not ingredients or not dosha:
        return redirect(url_for('select_categories'))

    # Perform grading logic
    results = []
    grade = 0
    total_ingredients = len(ingredients)

    for category, ingredient in ingredients.items():
        alternatives = get_alternative_ingredients(df, dosha, category, ingredient)
        if isinstance(alternatives, str):
            results.append(alternatives)
            grade += 1
        elif isinstance(alternatives, list) and alternatives:
            for alt in alternatives:
                results.append(f"Ingredient: {alt['Ingredient']}, Restricted Form: {alt['Restricted Form']}, Preferred Form: {alt['Preferred Form']}")
        else:
            results.append(f"No alternatives found for {ingredient} in {category}.")

    # Calculate final grade
    scaled_grade = (grade / total_ingredients) * 5 if total_ingredients > 0 else 0
    timestamp = datetime.now()

    # Fetch the logged-in user's email
    user_email = session.get('email')

    # Store the grading results in MongoDB
    try:
        mongo.db.users.update_one(
            {"email": user_email},
            {"$push": {
                "grading_results": {
                    "categories": categories,
                    "ingredients": ingredients,
                    "dosha": dosha,
                    "results": results,  # Store the results
                    "grade": scaled_grade,
                    "timestamp": timestamp
                }
            }}
        )
        flash('Grading results saved successfully!', 'success')
        return redirect(url_for('dashboard'))  # Redirect to the dashboard or another page
    except Exception as e:
        flash(f'Error storing grading results: {str(e)}', 'error')
        return redirect(url_for('select_categories'))


def get_alternative_ingredients(df, dosh, category, ingredient):
    if category not in df.columns or dosh.capitalize() not in df.columns:
        raise ValueError(f"Invalid category '{category}' or dosh '{dosh}'.")

    ingredient = ingredient.lower()
    match = df[(df[category] == 1) & (df[dosh.capitalize()] == 1)]

    if ingredient in match['Ingredient'].str.lower().values:
        restricted_info = \
        match[match['Ingredient'].str.lower() == ingredient][['Restricted Form', 'Preferred Form']].iloc[0]
        return f"The ingredient '{ingredient}' is already suitable. <br>Restricted: {restricted_info['Restricted Form']} <br>Preferred: {restricted_info['Preferred Form']}"

    alternatives = df[(df[dosh.capitalize()] == 1) & (df[category] == 1)]
    unique_alternatives = alternatives[~alternatives['Ingredient'].str.lower().duplicated()]

    result = []
    for _, row in unique_alternatives.iterrows():
        result.append({
            'Ingredient': row['Ingredient'],
            'Restricted Form': row['Restricted Form'],
            'Preferred Form': row['Preferred Form']
        })
        if len(result) >= 3:
            break

    return result

def get_categories():
    # Assuming df is your DataFrame loaded from the CSV/Excel file
    # Exclude non-category columns like 'Ingredient', 'Restricted Form', etc.
    excluded_columns = ['Ingredient', 'Restricted Form', 'Preferred Form', 'Vatta', 'Pitta', 'Kapha','Frequency']
    categories = [col for col in df.columns if col not in excluded_columns]
    return categories

@app.route('/grading/categories', methods=['GET'])
def get_categories_route():
    categories = get_categories()
    return render_template('partials/categories.html', categories=categories)

# About and other pages
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
