from flask import Flask, render_template, request, redirect, url_for, flash,session,jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import pandas as pd
from fuzzywuzzy import process
from collections import defaultdict
import re

app = Flask(__name__)
app.secret_key = 'ee541147b2d6c0f9c00de2090d566fe3e4ef1d816bdb8aa5c5100be7a1300a01'

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/annapurna"
mongo = PyMongo(app)
client = MongoClient('mongodb://localhost:27017/')
db = client.annapurna
collection = db.articles
user_collection = db.users
score_collection = db['score']

file_path = '/Users/shravyadsouza/Desktop/MIT/DE-minipro-ingredients.xlsx'
try:
    df = pd.read_excel(file_path)
    df.columns = [col.strip().title() for col in df.columns]  # Normalize column names to title case
    print("Columns in the DataFrame:", df.columns.tolist())  # Debugging step to check columns
except Exception as e:
    print(f"Error loading Excel file: {e}")
    raise FileNotFoundError(f"Could not load Excel file from path: {file_path}. Please check the file path and try again.")

required_columns = ['Ingredient', 'Restricted Form', 'Preferred Form', 'Vatta', 'Pitta', 'Kapha']
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    raise KeyError(f"The following required columns are missing in the DataFrame: {missing_columns}")

category_columns = ['Fruits', 'Vegetables', 'Grains', 'Legumes', 'Dairy', 'Animal Foods', 'Condiments',
                    'Nuts', 'Seeds', 'Oils', 'Beverages', 'Herbal Teas', 'Spices', 'Sweeteners', 'Food Supplements']

# Home (Landing Page) - Display Articles
@app.route('/')
def landing():
        articles = collection.find({}, {"title": 1, "content": 1})
        return render_template('landing.html', articles=articles)

# Signup page
@app.route('/signup',methods=['GET', 'POST'])
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
            session['email'] = email
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid password', 'error')
            return redirect(url_for('signin'))
    else:
        flash('User does not exist', 'error')
        return redirect(url_for('signin'))

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

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/mindfulness')
def mindfulness():
    return render_template('category.html')

@app.route('/articles')
def articles():
    return render_template('article.html')

@app.route('/about')
def about():
    return render_template('about.html')

def capitalize_first(text):
    """
    Capitalizes the first letter of a given text.
    If the text is None or empty, it returns it as is.
    """
    if text:
        return text.capitalize()
    return text

@app.route('/dashboard')
def dashboard():
    user_email = session.get('email', 't123@gmail.com')

    # Retrieve the user document for the given email
    user_data = db.users.find_one({"email": user_email})

    if user_data:
        # Extract necessary information with capitalization
        dominant_dosha = capitalize_first(user_data.get('dosha', 'Unknown'))
        blood_group = user_data.get('blood_group', 'N/A').upper()  # Keep blood group in uppercase (common style)
        age = user_data.get('age', 'N/A')
        gender = capitalize_first(user_data.get('gender', 'N/A'))

        return render_template(
            'dashboard.html',
            dominant_dosha=dominant_dosha,
            blood_group=blood_group,
            age=age,
            gender=gender
        )
    else:
        return "User data not found.", 404


@app.route('/dosha-quiz')
def dosha_quiz():
    return render_template('dosha-quiz.html')

@app.route('/ingredient_grade')
def ingredient_grade():
    """Display the main form with categories."""
    try:
        categories = category_columns
        return render_template('ingredient_grade.html', categories=categories)
    except Exception as e:
        print(f"Error displaying the home page: {e}")
        return "An error occurred while loading the home page. Please try again."

@app.route('/submit_dosha_quiz', methods=['POST'])
def submit_quiz():
    # Check if the user is logged in by checking the session
    if 'email' not in session:
        return redirect(url_for('signin'))  # Redirect to signin if the user is not logged in

    # Retrieve the logged-in user's email from the session
    email = session['email']
    timestamp = datetime.now()
    # Retrieve the form data (quiz answers)
    form_data = request.form

    # Create a dictionary to store the quiz answers
    user_answers = {
        'bodyType': form_data.get('bodyType'),
        'stressResponse': form_data.get('stressResponse'),
        'bodyTemperature': form_data.get('bodyTemperature'),
        'cheeks': form_data.get('cheeks'),
        'faceshape': form_data.get('faceshape'),
        'eyes': form_data.get('eyes'),
        'nose': form_data.get('nose'),
        'lips': form_data.get('lips'),
        'teeth': form_data.get('teeth'),
        'skin': form_data.get('skin'),
        'hair': form_data.get('hair'),
        'appetite': form_data.get('appetite'),
        'digestion': form_data.get('digestion'),
        'thirst': form_data.get('thirst'),
        'emotions': form_data.get('emotions'),
        'mind': form_data.get('mind'),
        'intellect': form_data.get('intellect'),
        'speech': form_data.get('speech'),
        'voice': form_data.get('voice'),
        'timestamp': timestamp  # Store the current timestamp
    }

    # Store the answers in MongoDB for the logged-in user
    try:
        # Update or insert the quiz answers for the user
        user_collection.update_one(
            {'email': email},  # Find the user by their email
            {'$set': {'quiz_answers': user_answers}}
        )

        # Run the aggregation to update dosha information
        db.users.aggregate([
            {
                '$project': {
                    '_id': 1,
                    'timestamp': 1,
                    'dosha': 1,
                    'quiz_answers': {'$ifNull': ['$quiz_answers', {}]},
                    'dosha_counts': {
                        '$cond': {
                            'if': {'$eq': [{'$type': '$quiz_answers'}, 'object']},
                            'then': {
                                '$reduce': {
                                    'input': {'$objectToArray': '$quiz_answers'},
                                    'initialValue': {'Vata': 0, 'Pitta': 0, 'Kapha': 0},
                                    'in': {
                                        'Vata': {
                                            '$cond': [
                                                {'$eq': ['$$this.v', 'Vata']},
                                                {'$add': ['$$value.Vata', 1]},
                                                '$$value.Vata'
                                            ]
                                        },
                                        'Pitta': {
                                            '$cond': [
                                                {'$eq': ['$$this.v', 'Pitta']},
                                                {'$add': ['$$value.Pitta', 1]},
                                                '$$value.Pitta'
                                            ]
                                        },
                                        'Kapha': {
                                            '$cond': [
                                                {'$eq': ['$$this.v', 'Kapha']},
                                                {'$add': ['$$value.Kapha', 1]},
                                                '$$value.Kapha'
                                            ]
                                        }
                                    }
                                }
                            },
                            'else': None
                        }
                    }
                }
            },
            {
                '$addFields': {
                    'maxDosha': {
                        '$cond': {
                            'if': {'$ne': ['$dosha_counts', None]},
                            'then': {
                                '$switch': {
                                    'branches': [
                                        {
                                            'case': {'$gt': ['$dosha_counts.Vata',
                                                             {'$max': ['$dosha_counts.Pitta', '$dosha_counts.Kapha']}]},
                                            'then': 'Vata'
                                        },
                                        {
                                            'case': {'$gt': ['$dosha_counts.Pitta',
                                                             {'$max': ['$dosha_counts.Vata', '$dosha_counts.Kapha']}]},
                                            'then': 'Pitta'
                                        },
                                        {
                                            'case': {'$gt': ['$dosha_counts.Kapha',
                                                             {'$max': ['$dosha_counts.Vata', '$dosha_counts.Pitta']}]},
                                            'then': 'Kapha'
                                        }
                                    ],
                                    'default': 'Kapha'
                                }
                            },
                            'else': None
                        }
                    }
                }
            },
            {
                '$addFields': {
                    'suggested_dominant_dosha': {
                        '$cond': {
                            'if': {'$ne': ['$dosha', 'NA']},
                            'then': '$dosha',
                            'else': {
                                '$cond': {
                                    'if': {'$ne': ['$maxDosha', None]},
                                    'then': '$maxDosha',
                                    'else': {
                                        '$arrayElemAt': [
                                            ['Vata', 'Pitta', 'Kapha'],
                                            {'$floor': {'$multiply': [{'$rand': {}}, 3]}}
                                        ]
                                    }
                                }
                            }
                        }
                    }
                }
            },
            {
                '$merge': {
                    'into': 'users',
                    'on': '_id',
                    'whenMatched': 'merge',
                    'whenNotMatched': 'insert'
                }
            }
        ])

        flash('Quiz submitted successfully! Kindly check your report', 'success')  # Flash success message
    except Exception as e:
        flash(f'Error submitting quiz: {str(e)}', 'error')  # Flash error message

    # Redirect to the dashboard after submission
    return redirect(url_for('dashboard'))


def filter_by_category_and_dosha(df, category, dosha_type):
    """Filter the DataFrame to include only ingredients that belong to the specified category and are suitable for the given dosha type."""
    if category not in df.columns or dosha_type not in df.columns:
        return pd.DataFrame()

    # Filter ingredients based on the category (category column value should be 1)
    category_filtered_df = df[df[category] == 1]

    # Further filter based on the dosha type (dosha column value should be 1)
    dosha_filtered_df = category_filtered_df[category_filtered_df[dosha_type] == 1]

    return dosha_filtered_df

def preprocess_ingredient_name(ingredient):
    """Preprocess the ingredient name by removing special characters, symbols, and converting it to lowercase."""
    return ingredient.lower().strip().capitalize()
def check_ingredient_suitability(df, ingredient, dosha_type, category):
    """
    Check if the entered ingredient is suitable for the selected dosha type.
    - If the Restricted Form is 'None', it is fully suitable.
    - If both Restricted and Preferred Forms are present, it is partially suitable.
    - If the Restricted Form is 'All', it is not suitable and suggests alternatives.
    """
    # Preprocess the ingredient name dynamically (capitalize first letter)
    ingredient = preprocess_ingredient_name(ingredient)
    df['Ingredient'] = df['Ingredient'].apply(preprocess_ingredient_name)  # Preprocess DataFrame ingredients

    # Step 1: Filter the DataFrame for the selected category, dosha type, and ingredient
    category_df = df[(df[category] == 1) & (df['Ingredient'] == ingredient) & (df[dosha_type] == 1)]

    # Step 2: Check if the ingredient exists for the dosha and determine suitability
    if not category_df.empty:
        preferred_form = category_df['Preferred Form'].values[0]
        restricted_form = str(category_df['Restricted Form'].values[0]).strip().lower()  # Convert to string

        # Case 1: Complete suitability if 'Restricted Form' is 'None'
        if restricted_form == 'none':
            suitability_message = f"The ingredient '{ingredient}' is completely suitable for '{dosha_type}' dosha."
            if pd.notnull(preferred_form) and preferred_form.lower() != 'none':
                suitability_message += f" Preferred form: {preferred_form}."
            return suitability_message, [], True

        # Case 2: Partial suitability if both 'Preferred Form' and 'Restricted Form' are present and not 'None'
        if pd.notnull(preferred_form) and restricted_form != 'none':
            suitability_message = (
                f"The ingredient '{ingredient}' is partially suitable for '{dosha_type}' dosha. "
                f"It is best consumed in the preferred form: {preferred_form}, while avoiding: {restricted_form}."
            )
            return suitability_message, [], True

        # Case 3: Not suitable if 'Restricted Form' is 'All'
        if restricted_form == 'all':
            return find_alternatives_fuzzy_only(df, ingredient, dosha_type, category)

    # Step 4: If the ingredient is not found or has no suitable match, find alternatives
    return find_alternatives_fuzzy_only(df, ingredient, dosha_type, category)


def find_alternatives_fuzzy_only(df, ingredient, dosha_type, category):
    """
    Find alternative ingredients in the same category that are suitable for the given dosha.
    Exclude ingredients with restricted forms unless explicitly required.
    Use fuzzy matching to suggest alternatives dynamically.
    Only include fuzzy matches with a score ≥ 50 or ingredients with no restricted form.
    Ensure alternatives are unique for each category.
    """
    # Filter suitable ingredients in the same category for the given dosha type
    suitable_df = filter_by_category_and_dosha(df, category, dosha_type)

    # If no suitable alternatives found, return no alternatives
    if suitable_df.empty:
        return f"No suitable alternatives found for '{ingredient}'.", [], False

    # Normalize the input ingredient (to handle plural forms and case)
    normalized_input = ingredient.lower().rstrip('s')

    # Use fuzzy matching to find close matches in the cleaned/preprocessed ingredient names
    all_ingredients = suitable_df['Ingredient'].tolist()
    fuzzy_matches = process.extract(ingredient, all_ingredients, limit=10, scorer=process.fuzz.ratio)

    # Prepare the alternatives list for display, ensuring fuzzy score ≥ 50 and including those with no restriction
    alternatives = set()  # Using a set to store unique alternatives
    for fuzzy_match in fuzzy_matches:
        ingredient_name, fuzzy_score = fuzzy_match

        # Normalize the fuzzy match ingredient
        normalized_match = ingredient_name.lower().rstrip('s')

        # Exclude the original ingredient and its variations (like plural forms) from the list of alternatives
        if normalized_match == normalized_input:
            continue

        row = suitable_df[suitable_df['Ingredient'] == ingredient_name].iloc[0]

        # Check for restricted form starting with 'n' (ignoring case) or empty/null values
        restricted_form = row['Restricted Form']
        if fuzzy_score >= 50 or pd.isnull(restricted_form) or restricted_form.strip().lower().startswith('n'):
            alt_message = f"{ingredient_name.title()} (Fuzzy Score: {fuzzy_score:.2f})"
            if pd.notnull(row['Preferred Form']):
                alt_message += f", Preferred form: {row['Preferred Form']}"

            # Add only unique alternatives to the set
            alternatives.add(alt_message)

    # If no suitable alternatives are found without restricted forms, display a message
    if not alternatives:
        return f"No suitable alternatives found for '{ingredient}' that are fully compatible with the '{dosha_type}' dosha.", [], False

    # Convert the set to a list and return it as part of the result
    return f"The ingredient '{ingredient}' is not suitable for the '{dosha_type}' dosha.", list(alternatives), False

@app.route('/submit_ingredient_grade', methods=['POST'])
def submit_ingredient_quiz():
    """Process the form submission and generate the result based on input, including grading."""
    try:
        # Retrieve user inputs from form submission
        dosha = request.form.get('dosha', '').strip().capitalize()
        categories = request.form.get('categories', '').strip().split(',')

        if not dosha or not categories:
            return "Invalid input. Please ensure you have selected categories and dosha."

        total_ingredients = 0
        suitable_ingredients = 0
        results = []

        # Process each category and its respective ingredients
        for category in categories:
            ingredient_input = request.form.get(f'{category}_ingredient', '').strip()
            if ingredient_input:
                ingredients_list = [ing.strip() for ing in ingredient_input.split(',')]
                total_ingredients += len(ingredients_list)

                for ingredient in ingredients_list:
                    # Check suitability for each ingredient
                    suitability_message, alternatives, is_suitable = check_ingredient_suitability(
                        df, ingredient, dosha, category
                    )

                    # Create a structured result object
                    result_entry = {
                        "category": category.capitalize(),
                        "ingredient": ingredient.capitalize(),
                        "suitability": suitability_message,
                        "preferred_form": "",
                        "restricted_form": "",
                        "alternatives": alternatives if not is_suitable else []
                    }

                    # Track preferred and restricted forms if suitable
                    if is_suitable:
                        suitable_ingredients += 1
                        suitable_rows = df[
                            (df['Ingredient'].str.lower() == ingredient.lower()) & (df[category] == 1)
                        ]
                        if not suitable_rows.empty:
                            result_entry["preferred_form"] = suitable_rows['Preferred Form'].values[0] or ""
                            result_entry["restricted_form"] = suitable_rows['Restricted Form'].values[0] or ""

                    results.append(result_entry)

        # Calculate the percentage of suitable ingredients
        percentage_suitable = (
            (suitable_ingredients / total_ingredients) * 100 if total_ingredients > 0 else 0
        )

        # Assign a grade based on the percentage of suitable ingredients
        grade = (
            5 if percentage_suitable >= 81 else
            4 if percentage_suitable >= 61 else
            3 if percentage_suitable >= 41 else
            2 if percentage_suitable >= 21 else
            1
        )

        # Store the result in the "score" collection with a unique timestamp
        if 'email' in session:
            score_collection = db.score
            email = session['email']
            timestamp = datetime.now()

            # Ensure the document exists with an empty 'scores' array if new
            score_collection.update_one(
                {'email': email},
                {
                    '$setOnInsert': {'email': email, 'scores': []}
                },
                upsert=True
            )

            # Create the score data structure
            score_data = {
                'dosha': dosha,
                'categories': categories,
                'results': results,
                'grade': grade,
                'timestamp': timestamp
            }

            # Push the new score_data into the 'scores' array
            try:
                result = score_collection.update_one(
                    {'email': email},
                    {'$push': {'scores': score_data}}
                )
                print(f"Score data inserted for email {email}: {score_data}")
                print(f"Update result: {result.modified_count} document(s) modified.")
            except Exception as e:
                print(f"Error during database update: {e}")

        # Prepare the response for display
        """response_lines = []
        for result in results:
            response_lines.append(f"{result['category']} - {result['ingredient']}: {result['suitability']}")
            if result['alternatives']:
                response_lines.append("Suggested alternatives:")
                response_lines.extend([f"  - {alt}" for alt in result['alternatives']])

        # Add the overall grade to the response
        response_lines.append(f"<br><strong>Your Dosha Suitability Grade:</strong> {grade}/5")

        return "<br>".join(response_lines)"""

        # Flash a success message and redirect to the dashboard
        flash("Submission successful! Check your report for detailed results.", "success")
        return redirect(url_for('dashboard'))

    except Exception as e:
        print(f"Error processing submission: {e}")
        flash("An error occurred while processing your submission. Please try again.", "error")
        return redirect(url_for('dashboard'))

def extract_forms(suitability):
    """
    Extracts preferred form and restricted form from the suitability text using regex.
    """
    # Extract preferred form using regex
    preferred_form_match = re.search(r'preferred form: (.*?)(,|\.|$)', suitability, re.IGNORECASE)
    preferred_form = preferred_form_match.group(1) if preferred_form_match else "Not specified"

    # Extract restricted form using regex
    restricted_form_match = re.search(r'avoiding: (.*?)(,|\.|$)', suitability, re.IGNORECASE)
    restricted_form = restricted_form_match.group(1) if restricted_form_match else "None"

    return preferred_form, restricted_form


def capitalize_words(text):
    """
    Capitalizes the first letter of each word in a given text.
    """
    if text:
        return ' '.join(word.capitalize() for word in text.split())
    return text


def preprocess_score_data(user_score):
    """
    Process the score data for display, including extracting preferred and restricted forms,
    and simplifying the suitability message. Displays alternatives only when the ingredient
    is not suitable, and sets 'Restricted Form: All' for such cases.
    """
    if not user_score or 'scores' not in user_score:
        return None

    # Extract the latest score entry
    latest_score = user_score['scores'][-1]
    dosha = latest_score.get("dosha", "Unknown")
    categories = latest_score.get("categories", [])

    # Create a dictionary to organize results by category
    category_results = defaultdict(list)

    for result in latest_score.get("results", []):
        ingredient = result.get("ingredient", "Unknown")
        suitability = result.get("suitability", "No suitability information.")

        # Extract forms from suitability text
        preferred_form, restricted_form = extract_forms(suitability)

        # Simplify the suitability message
        if preferred_form == "All" and (restricted_form is None or restricted_form.lower() == 'nan'):
            suitability_status = "Completely Suitable"
        elif "not suitable" in suitability.lower():
            suitability_status = "Not Suitable"
        elif "partially suitable" in suitability.lower():
            suitability_status = "Partially Suitable"
        else:
            suitability_status = "Unknown Suitability"

        # Process alternatives only if the ingredient is "Not Suitable"
        alternatives = result.get("alternatives", [])
        if suitability_status == "Not Suitable" and alternatives:
            # Remove the fuzzy score part from each alternative string
            alternatives_formatted = ", ".join([alt.split(" (")[0] for alt in alternatives])
        else:
            alternatives_formatted = "None"

        # Capitalize words in preferred and restricted forms
        preferred_form = capitalize_words(preferred_form)
        restricted_form = capitalize_words(restricted_form)

        # Adjust for "Not Suitable" ingredients
        if suitability_status == "Not Suitable":
            preferred_form = None  # Do not display preferred form
            restricted_form = "All"

        # Add the processed result to the category_results dictionary
        refined_result = {
            "ingredient": ingredient,
            "suitability": suitability_status,
            "preferred_form": preferred_form,
            "restricted_form": restricted_form,
            "alternatives": alternatives_formatted
        }
        category_results[result.get("category", "Unknown")].append(refined_result)

    grade = latest_score.get("grade", "N/A")

    return {
        "dosha": dosha,
        "categories": categories,
        "category_results": category_results,
        "grade": grade
    }
@app.route('/ayurvedic-report')
def ayurvedic_report():
    user_email = session.get('email')

    # Retrieve the user document for the given email
    user_data = db.users.find_one({"email": user_email})

    if user_data:
        # Extract necessary information
        dosha_counts = user_data.get('dosha_counts', {'Vata': 0, 'Pitta': 0, 'Kapha': 0})
        max_dosha = user_data.get('maxDosha', 'Unknown')
        suggested_dominant_dosha = user_data.get('suggested_dominant_dosha', 'Unknown')

        # Retrieve the latest score document for the user for grading
        user_score = score_collection.find_one({"email": user_email}, sort=[("timestamp", -1)])
        processed_data = preprocess_score_data(user_score)

        return render_template(
            'report.html',
            dosha_counts=dosha_counts,
            max_dosha=max_dosha,
            suggested_dominant_dosha=suggested_dominant_dosha,
            dosha=processed_data['dosha'],
            categories=processed_data['categories'],
            category_results=processed_data['category_results'],
            grade=processed_data['grade']
        )
    else:
        return "User data not found.", 404

@app.route('/guidelines')
def guidelines():
    return render_template('guidelines.html')

@app.route('/logout')
def logout():
    return render_template('landing.html')

@app.route('/from_about')
def from_about():
    return render_template('landing.html')

if __name__ == '__main__':
    app.run(debug=True)

