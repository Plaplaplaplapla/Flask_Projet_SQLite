from flask import Flask, render_template_string, render_template, jsonify, request, redirect, url_for, session
from flask import render_template
from flask import json
from urllib.request import urlopen
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)                                                                                                                  
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# -----------------------------
# FONCTIONS UTILES
# -----------------------------

def est_authentifie():
    """Vérifie si un utilisateur est connecté"""
    return session.get('authentifie')


def est_admin():
    """Vérifie si l'utilisateur est admin"""
    return session.get('role') == 'admin'


# -----------------------------
# ROUTES PRINCIPALES
# -----------------------------

@app.route('/')
def accueil():
    return render_template('acceuil.html')


# -----------------------------
# AUTHENTIFICATION
# -----------------------------

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Admin
        if username == 'admin' and password == 'password':
            session['authentifie'] = True
            session['role'] = 'admin'
            return redirect(url_for('accueil'))

        # Utilisateur classique
        elif username == 'user' and password == '12345':
            session['authentifie'] = True
            session['role'] = 'user'
            return redirect(url_for('accueil'))

        # Mauvais identifiants
        return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('accueil'))


# -----------------------------
# GESTION DES CLIENTS
# -----------------------------

@app.route('/fiche_nom/', methods=['GET', 'POST'])
def fiche_nom():
    if not est_authentifie():
        return redirect(url_for('authentification'))

    data = []
    if request.method == 'POST':
        nom = request.form['nom']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clients WHERE nom = ?', (nom,))
        data = cursor.fetchall()
        conn.close()

    return render_template('recherche_nom.html', data=data)


@app.route('/consultation/')
def ReadBDD():
    if not est_authentifie():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients;')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)


@app.route('/fiche_client/<int:post_id>')
def Readfiche(post_id):
    if not est_authentifie():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (post_id,))
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)


@app.route('/enregistrer_client', methods=['GET', 'POST'])
def enregistrer_client():
    if not est_authentifie():
        return redirect(url_for('authentification'))

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
        return redirect(url_for('ReadBDD'))

    return render_template('formulaire.html')


# -----------------------------
# GESTION DES LIVRES
# -----------------------------

@app.route('/livres/')
def lire_livres():
    if not est_authentifie():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM livres;')
    livres = cursor.fetchall()
    conn.close()
    return render_template('livres.html', livres=livres)


@app.route('/ajouter_livre', methods=['GET', 'POST'])
def ajouter_livre():
    if not est_authentifie() or not est_admin():
        return redirect(url_for('authentification'))

    if request.method == 'POST':
        titre = request.form['titre']
        auteur = request.form['auteur']
        stock = int(request.form['stock'])
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO livres (titre, auteur, stock) VALUES (?, ?, ?)',
            (titre, auteur, stock)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('lire_livres'))

    return render_template('ajouter_livre.html')


# -----------------------------
# GESTIONNAIRE DE TÂCHES
# -----------------------------

@app.route('/tasks')
def tasks():
    if not est_authentifie():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    tasks = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return render_template('tasks.html', tasks=tasks)


@app.route('/ajouter_task', methods=['POST'])
def ajouter_task():
    if not est_authentifie():
        return redirect(url_for('authentification'))

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


# -----------------------------
# RUN
# -----------------------------

if __name__ == "__main__":
    app.run(debug=True)
