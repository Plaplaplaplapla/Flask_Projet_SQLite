from flask import Flask, render_template_string, render_template, jsonify, request, redirect, url_for, session
from flask import render_template
from flask import json
from urllib.request import urlopen
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)                                                                                                                  
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# ---------- AUTH ----------

def est_authentifie():
    return session.get('authentifie')

def est_user_authentifie():
    return session.get('user_auth')

# ---------- ROUTES ----------

@app.route('/')
def hello_world():
    return render_template('acceuil.html')

@app.route('/lecture')
def lecture():
    if not est_authentifie():
        return redirect(url_for('authentification'))
    return "<h2>Bravo, vous êtes authentifié</h2>"

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Vérification admin
        if username == 'admin' and password == 'password':
            session['authentifie'] = True
            session['role'] = 'admin'
            return redirect(url_for('hello_world'))

        # Vérification utilisateur classique
        elif username == 'user' and password == '12345':
            session['authentifie'] = True
            session['role'] = 'user'
            return redirect(url_for('hello_world'))

        # Mauvais identifiants
        else:
            return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)



# ---------- FICHE NOM ----------

@app.route('/fiche_nom/', methods=['GET', 'POST'])
def fiche_nom():
    if not est_authentifie():
        return redirect(url_for('authentification'))  # plus 'auth_user'

    data = []

    if request.method == 'POST':
        nom = request.form['nom']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clients WHERE nom = ?', (nom,))
        data = cursor.fetchall()
        conn.close()

    return render_template('recherche_nom.html', data=data)

# ---------- BDD ----------

@app.route('/consultation/')
def ReadBDD():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients;')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/fiche_client/<int:post_id>')
def Readfiche(post_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (post_id,))
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/enregistrer_client', methods=['GET', 'POST'])
def enregistrer_client():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO clients (created, nom, prenom, adresse) VALUES (?, ?, ?, ?)',
            (1002938, nom, prenom, "ICI")
        )
        conn.commit()
        conn.close()
        return redirect('/consultation/')

    return render_template('formulaire.html')


@app.route('/livres/')
def lire_livres():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM livres;')
    livres = cursor.fetchall()
    conn.close()
    return render_template('livres.html', livres=livres)





# Ajouter un livre
@app.route('/ajouter_livre', methods=['GET', 'POST'])
def ajouter_livre():
    if request.method == 'POST':
        titre = request.form['titre']
        auteur = request.form['auteur']
        stock = int(request.form['stock'])
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO livres (titre, auteur, stock) VALUES (?, ?, ?)', (titre, auteur, stock))
        conn.commit()
        conn.close()
        return redirect('/livres/')
    return render_template('ajouter_livre.html')
    
##Gestionnaire
@app.route('/tasks')
def tasks():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    tasks = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return render_template('tasks.html', tasks=tasks)

@app.route('/ajouter_task', methods=['POST'])
def ajouter_task():
    title = request.form.get('title')
    description = request.form.get('description')
    status = request.form.get('status', 'pending')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO tasks (title, description, status) VALUES (?, ?, ?)',
        (title, description, status)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('tasks'))



# ---------- RUN ----------

if __name__ == "__main__":
    app.run(debug=True)

