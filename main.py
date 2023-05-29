from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3


app = Flask(__name__)
app.secret_key = "mysecretkey"

con = sqlite3.connect("db.db")
cur = con.cursor()

user_query = """
            CREATE TABLE IF NOT EXISTS User 
            (
                username TEXT PRIMARY KEY NOT NULL, 
                password TEXT NOT NULL,
                CHECK (length(username) > 0)
            )
            """
cur.execute(user_query)

score_query = """
            CREATE TABLE IF NOT EXISTS Highscore 
            (
                username TEXT PRIMARY KEY NOT NULL, 
                score INT NOT NULL DEFAULT 0,
                CHECK (score > 0),
                CHECK (length(username) > 0)
                FOREIGN KEY (username) REFERENCES USER(username)
            )
            """
cur.execute(score_query)

# friend_query = """
#             CREATE TABLE IF NOT EXISTS Friends 
#             (
#                 username TEXT PRIMARY KEY NOT NULL, 
#                 friend_username TEXT NOT NULL,
# 								CHECK (length(username) > 0),
# 								CHECK (length(friend_username) > 0)
#                 FOREIGN KEY (username) REFERENCES User(username)
#                 FOREIGN KEY (friend_username) REFERENCES User(username)
#             )
#             """
# cur.execute(friend_query)

con.commit()
con.close()

# starting page
@app.route('/')
def index():
	# if "hex_to_bin" not in session:
	# 	# two game modes, default is hex to bin
	# 	session["hex_to_bin"] = True
	
	return render_template("hex_to_bin_start.html")

# main game
@app.route('/game')
def game():
	return render_template("hex_to_bin.html")


@app.route('/instructions')
def instructions():
	return render_template("instructions.html")

# page shown after game finishes
@app.route('/game-over')
def game_over():
	return render_template("game_over.html")

# highscores page
@app.route('/highscores')
def highscores():
	get_all_scores_query = "SELECT * FROM Highscore ORDER by score DESC;"
	
	con = sqlite3.connect("db.db")
	cur = con.cursor()
	
	highscores = cur.execute(get_all_scores_query).fetchall()
	
	return render_template("highscores.html", highscores=highscores)

# helper endpoint to update highscore
@app.route('/submit_score', methods=['POST'])
def submit_score():
	score = request.form['score']
	score = int(score)
	
	# check if user is logged in
	if "username" in session and score > 0:
		username = session["username"]
		get_old_score_query = f"SELECT * FROM Highscore WHERE username = '{username}';"
		
		insert_new_score_query = f"INSERT INTO Highscore VALUES ('{username}','{score}');"
		update_score_query = f"UPDATE Highscore SET score = '{score}' WHERE username = '{username}';"
		
		con = sqlite3.connect("db.db")
		cur = con.cursor()
		cur.execute(get_old_score_query)
		user_score_data = cur.fetchone()
		if user_score_data:
			# check if score is higher
			if score > user_score_data[1]:
				cur.execute(update_score_query)
		else:
			cur.execute(insert_new_score_query)
		con.commit()
		
	return "success"


@app.route('/register', methods=['POST', 'GET'])
def register():
	if(request.method == "POST"):
		username = request.form['username']
		password = request.form['password']
		get_same_user_query = f"SELECT * FROM User WHERE username = '{username}';"
		insert_new_user_query = f"INSERT INTO User VALUES ('{username}','{password}');"
		
		con = sqlite3.connect("db.db")
		cur = con.cursor()
		cur.execute(get_same_user_query)
		old_user = cur.fetchone()
		if old_user:
			flash("Username already exists")
			return render_template('register.html')
		else:
			cur.execute(insert_new_user_query)
			con.commit()
			session["username"] = username
			return redirect(url_for('index'))
	else:
		return render_template('register.html')


@app.route('/profile')
def profile():
	if 'username' not in session:
		return "You are not logged in."

	username = session["username"]
	high_score_query = f"SELECT * FROM Highscore WHERE username = '{username}';"

	con = sqlite3.connect("db.db")
	cur = con.cursor()
	highscore_data = cur.execute(high_score_query).fetchone()
	highscore = highscore_data[1] if highscore_data else 0

	return render_template('profile.html',username=username,highscore=highscore)
	
# @app.route('/add-friends', methods=['POST', 'GET'])
# def add_friends():
# 	if 'username' not in session:
# 		return "You are not logged in."

# 	search_query = request.args.get('search_query')
# 	print(search_query)
# 	user_search_query = f"SELECT username FROM User WHERE username LIKE '{search_query}%';"
	
# 	con = sqlite3.connect("db.db")
# 	cur = con.cursor()
# 	users = cur.execute(user_search_query).fetchall()
# 	users = [user[0] for user in users if user[0] != session["username"]]
	
# 	return render_template('add_friends.html', users=users)

# @app.route('/add_friend', methods=['POST'])
# def add_friend():
# 	friend = request.form['user_id']
# 	username = session["username"]
	
# 	add_friends_query1 = f"INSERT INTO Friends VALUES ('{username}','{friend}');"
# 	add_friends_query2 = f"INSERT INTO Friends VALUES ('{friend}','{username}');"
	
# 	con = sqlite3.connect("db.db")
# 	cur = con.cursor()
# 	cur.execute(add_friends_query1)
# 	cur.execute(add_friends_query2)
# 	con.commit()
# 	return "added friend successfully"

	
@app.route('/login', methods=['POST', 'GET'])
def login():
	if(request.method == "POST"):
		username = request.form['username']
		password = request.form['password']
		sql_query = f"SELECT username, password FROM User WHERE username = '{username}';"
		con = sqlite3.connect("db.db")
		cur = con.cursor()
		user = cur.execute(sql_query).fetchone()
		if not user:
			flash("No such user: " + username)
			return render_template("login.html")
		elif password != user[1]:
			flash("Wrong password")
			return render_template("login.html")
		else:
			# login success
			session["username"] = username
			return render_template("hex_to_bin_start.html")
	else:
		return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('username', None)
    
    return redirect(url_for('index'))

# @app.route('/test')
# def test():
# 		con = sqlite3.connect("db.db")
# 		cur = con.cursor()
# 		res = cur.execute("SELECT * FROM User;").fetchall()
# 		print("users", res)
# 		res = cur.execute("SELECT * FROM Highscore;").fetchall()
# 		print("scores", res)
# 		return "testing"
		

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=82)