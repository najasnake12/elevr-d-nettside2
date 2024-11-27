# made by najasnake12
# better known as the -10x developer

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import logging
import sqlite3
from flask_mail import Mail, Message
from flask_session import Session
import os
import secrets

app = Flask(__name__)

english_words_global = ['dope', 'omg', 'simp', 'cringe']
common_typos = ['adresse', 'aggressiv', ' nettop', 'nyskjerrig', 'igang', 'istedet', 'utrykk', 'tilegg', 'desverre', 'kansjke', 'etterhvert', 'ifjor', 'ihvertfall', 'epost', 'interesert', 'interesant', 'sannsynelig', 'sansynlig', 'sansynnlig', 'sjangse', 'baler', 'skjekke', 'leke stativ', 'sand kasse', 'fotbalbane', 'fotbal', 'basketbal', 'hokey', 'hocey', 'spesiellt', 'iriterende', 'sinnt', 'såvidt', 'interisert']

editor_database_file_global = 'editor_database.txt'
image_database_global = 'C:/Users/krist/Desktop/School council project/image_database'

passwords = {}

def load_passwords():
    """Load passwords from a file and store them in the global passwords dictionary."""
    global passwords
    try:
        with open("passwords.txt", "r") as file:
            for line in file.readlines():
                key, value = line.strip().split("=")
                passwords[key] = value
    except FileNotFoundError as e:
        errorlogger.error(f'Error loading passwords: {e}')


load_passwords()

app.secret_key = secrets.token_urlsafe(16)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'holmenskoletest@gmail.com'
app.config['MAIL_PASSWORD'] = passwords.get("MAIL_PASSWORD", "")
app.config['MAIL_DEFAULT_SENDER'] = 'holmenskoletest@gmail.com'

mail = Mail(app)

# Setup error logger
errorlogger = logging.getLogger('errorlogger')
errorlogger.setLevel(logging.DEBUG)
fh = logging.FileHandler('errorlogger.log')
fh.setLevel(logging.DEBUG)
errorlogger.addHandler(fh) 


@app.route('/')
def index():
    session['logged_in'] = False
    session['editor_login_session'] = False
    return render_template('index.html')

@app.route('/submit_form', methods=['POST'])
def submit_form():
    # this function is *really* optmized for speed.
    # please do not change ANYTHING in this function, even the smallest details are there for a reason.
    # I don't wanna use async
    # PLEASE: do not say that I should use 'or' instead of if statements at line 49-52, I have tested it,
    # it is indeed faster :)
    # -me
    english_words_local = english_words_global
    mail_local_var = mail
    common_typos_local_var = common_typos
    
    
    if request.method == 'POST':
        try:
            student_name, student_class, student_proposal = request.form['student_name'], request.form['student_class'], request.form['student_proposal']

            if student_name == '':
                student_name = 'Anonym'
            if student_class == '':
                student_class = 'Lærer'
                
            # this code (below) is not optimized, feel free to make it so

            # if somebody is in the 4th grade (or lower), they don't have to worry about typos.
            if int(student_class[0]) <= 4:  # Assuming the grade is always a number at the beginning of the string
                pass
            else:
                if not(student_proposal.endswith('.') or student_proposal.endswith('?') or student_proposal.endswith('!')):
                    return render_template('for_mange_skrivefeil.html')
            
                if not student_proposal[0].isupper():
                    return render_template('for_mange_skrivefeil.html')
            
                if any(word in student_proposal for word in english_words_local):
                    return render_template('for_mange_skrivefeil.html')
            
                if any(typo in student_proposal for typo in common_typos_local_var):
                    return render_template('for_mange_skrivefeil.html')
            
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO forms_submitted (student_name, student_class, student_proposal)
                      VALUES (?, ?, ?)''', (student_name, student_class, student_proposal))
                conn.commit()
            # below this comment, the code is optmized

                # send the mail
                with mail_local_var.connect() as conn:
                    recipient_email = "pessiartist@gmail.com"  # change this, "pessiartist@gmail.com" is for testing.
                    msg = Message(f"Nytt Forslag", recipients=[recipient_email])
                    msg.body = f'{student_name}, {student_class}, {student_proposal}'
                    mail_local_var.send(msg)

                return redirect(url_for('success'))
        except (KeyError, SyntaxError, sqlite3.OperationalError, sqlite3.IntegrityError, sqlite3.DatabaseError, AttributeError, ConnectionError, ValueError) as e:
            errorlogger.error(f'Error: {e}')
            return render_template('error.html')

@app.route('/delete_proposal/<int:proposal_id>', methods=['GET'])
def delete_proposal(proposal_id):
    try:
        with sqlite3.connect('database.db') as conn:
            conn.execute('DELETE FROM forms_submitted WHERE id = ?', (proposal_id,))
            conn.commit()
    except BaseException as e:
        errorlogger.error(f'Error: {e}')
        return render_template('error.html')
    
    return redirect(url_for('admin_panel'))


@app.route('/editor_login', methods=['GET', 'POST'])
def editor_login():
    if request.method == 'POST':
        entered_username = request.form['editor_username']
        entered_password = request.form['editor_password']

        if entered_username == 'admin' and entered_password == passwords.get('EDITOR_PASSWORD'):
            session['editor_login_session'] = True
            return render_template('editor_page.html')
        else:
            return render_template('error_admin_login.html')
    

    return render_template('editor_login.html')

# VOTING ROUTES

# HOW TO MAKE A NEW VOTING, OR UPDATE THE CURRENT VOTING:
# 1. On line "177", change "1", and/or "2" (or whatever they are named), to the name of your liking.
# 2. On line "186" change "1" and/or "2" (or whatever they are named), to the same name as line "177".
# 3. On line "210" change "1" (in the votes["1"] ) to the same name as line "177".
# 4. On line "227" change "2" (in the votes["2"] ) to the same name as line "177".
# 5. Open "voting.html" and change the voting names (as well as the variables) to the same name as line "177" in the Python file. (The Python file is the file you're reading this in)
# 6 IMPORTANT: When a voting is finished, and a new one is starting; make sure that you delete ALL the ip addresses from "ip_addresses.txt"
# 7. IMPORTANT: Inside the "voting_database.txt" file, remember to change "1" and/or "2" to the current names of the different votings. And it's also important to reset the votes to 0; not just delete them.
# 8. IMPORTANT: This code may change, remember to keep updating the lines (the lines to edit) in this "guide".


VOTE_FILE = 'voting_database.txt'
IP_FILE = 'ip_addresses.txt'

def person_has_voted(ip_address, ip_file):
    with open(ip_file, 'r') as file:
        if ip_address + '\n' in file.readlines():
            return render_template('you_have_voted.html')
    return None

def read_votes():
    """Reads the vote counts from the voting file."""
    votes = {"1": 0, "2": 0}
    if os.path.exists(VOTE_FILE):
        with open(VOTE_FILE, 'r') as file:
            for line in file:
                choice, count = line.strip().split(":")
                votes[choice] = int(count.strip())  # store the votes
    else:
        # If the file doesn't exist, create it with default votes "0"
        with open(VOTE_FILE, 'w') as file:
            file.write("1: 0\n2: 0\n")
    return votes

def write_votes(votes):
    """Writes the updated vote counts to the file."""
    with open(VOTE_FILE, 'w') as file:
        for choice, count in votes.items():
            file.write(f"{choice}: {count}\n")

@app.route('/voting')
def voting():
    # Read the votes from the file
    votes = read_votes()
    return render_template('voting.html', votes=votes)

@app.route('/vote1', methods=['POST'])
def vote1():
    ip_address = request.remote_addr
    
    if person_has_voted(ip_address, IP_FILE): 
        return render_template('you_have_voted.html')
    
  
    votes = read_votes()
    votes["1"] += 1
    write_votes(votes)
    
   
    with open(IP_FILE, 'a') as file:
        file.write(f"{ip_address}\n")
    
    return redirect('/voting')

@app.route('/vote2', methods=['POST'])
def vote2():
    ip_address = request.remote_addr
    
    if person_has_voted(ip_address, IP_FILE): 
        return render_template('you_have_voted.html')
    
    votes = read_votes()
    votes["2"] += 1
    write_votes(votes)
    
    with open(IP_FILE, 'a') as file:
        file.write(f"{ip_address}\n")
    
    return redirect('/voting')

##############

@app.route('/editor_page', methods=['GET', 'POST'])
def editor_page():
    if not session.get('editor_login_session'):
        return render_template('easteregg.html')

    editor_database_file_local = editor_database_file_global
    image_database_local = image_database_global

    if request.method == 'POST':
        try:
            title = request.form['title']
            description = request.form['description']
            content = request.form['content']
            image = request.files['image']

            image_filename = None

            if image:
                # Construct the image path by prepending 'static/' and saving it to the 'static/image_database' folder
                image_filename = os.path.join('static', 'image_database', image.filename)

                # Save the image to the 'static/image_database' folder
                image.save(image_filename)

            # Prepare the article filename (e.g., article about 'My New Article' becomes 'my_new_article.html')
            article_filename = f"{title.replace(' ', '_').lower()}.html"
            article_path = os.path.join('articles', article_filename)

            with open(article_path, 'w') as article_file:
                article_file.write(f'''
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>{title}</title>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
                    <link rel="stylesheet" href="/static/styles.css"> <!-- Link to custom CSS -->
                </head>
                <body class="bg-light">
                    <header class="bg-primary text-white py-5 text-center">
                        <h1>{title}</h1>
                    </header>
                    <div class="container py-5">
                        <div class="row justify-content-center">
                            <div class="col-md-8">
                                <div class="card shadow-lg mb-5">
                                    <div class="card-body">
                                        {f'<img src="/static/image_database/{image.filename}" class="img-fluid mb-4" alt="{title}">' if image_filename else ''}
                                        <h3 class="card-title">{title}</h3>
                                        <p class="text-muted mb-4">{description}</p>
                                        <div class="content">{content}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <footer class="bg-dark text-white py-3 text-center">
                        <p class="mb-0">Made with love by <a href="https://github.com/najasnake12" class="text-white">Najasnake12</a></p>
                    </footer>
                    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.6/dist/umd/popper.min.js"></script>
                    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.min.js"></script>
                </body>
                </html>
                ''')

            with open(editor_database_file_local, 'a') as file:
                file.write(f'{title},{description},{article_filename}\n')

        except Exception as e:
            errorlogger.error(f'Error: {e}')
            return render_template('error.html')

    return render_template('editor_page.html')


@app.route('/articles/<filename>')
def article(filename):
    article_path = os.path.join('articles', filename)

    try:
        with open(article_path, 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return render_template('error.html')


@app.route('/news')
def news():
    articles = []
    try:
        with open(editor_database_file_global, 'r') as file:
            for line in file:
                title, description, filename = line.strip().split(',')
                image_filename = filename.replace('.html', '.jpg')
                articles.append({'title': title, 'description': description, 'filename': filename, 'image': image_filename})

    except Exception as e:
        errorlogger.error(f'Error: {e}')
        return render_template('error.html')

    return render_template('news.html', articles=articles)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        entered_password = request.form['admin_password']
        entered_username = request.form['admin_username']
        
        if entered_password == passwords.get('ADMIN_PASSWORD') and entered_username == 'admin':  
            session['logged_in'] = True
            session['show_delete_button'] = True  # store in session
            return redirect(url_for('admin_panel'))
        
        elif entered_password == passwords.get('ADMIN_PASSWORD') and entered_username == 'teacher':
            session['logged_in'] = True
            session['show_delete_button'] = False  # store in session
            return redirect(url_for('admin_panel'))
        
        else:
            return render_template('error_admin_login.html')
        
    return render_template('admin_login.html')

@app.route('/admin_panel', methods=['GET'])
def admin_panel():
    if not session.get('logged_in'):
        return render_template('easteregg.html')  # show the easter egg if not logged in

    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        data = cursor.execute('SELECT * FROM forms_submitted').fetchall()
        conn.close()
        show_delete_button = session.get('show_delete_button', False)
    except BaseException as e:
        errorlogger.error(f'Error: {e}')
        return render_template('error.html')

    return render_template('admin_panel.html', data=data, show_delete_button=show_delete_button)


@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/najasnake12')
def najasnake12():
    return redirect('https://github.com/najasnake12')

if __name__ == '__main__':
    app.run(debug=True)