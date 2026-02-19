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
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # On récupère l'utilisateur en base
        cursor.execute(
            'SELECT id, username, password, role FROM utilisateurs WHERE username = ?',
            (username,)
        )
        user = cursor.fetchone()
        conn.close()

        # user = (id, username, password_db, role)
        if user and user[2] == password:
            session['authentifie'] = True
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            return redirect(url_for('accueil'))

        return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('accueil'))



# Route pour afficher la liste des utilisateurs
@app.route('/utilisateurs/')
def liste_utilisateurs():
    if not est_authentifie() or not est_admin():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, role FROM utilisateurs')
    utilisateurs = cursor.fetchall()
    conn.close()

    return render_template('liste_utilisateurs.html', utilisateurs=utilisateurs)


# Route pour ajouter un utilisateur
@app.route('/ajouter_utilisateur', methods=['GET', 'POST'])
def ajouter_utilisateur():
    if not est_authentifie() or not est_admin():
        return redirect(url_for('authentification'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'user')

        if not username or not password:
            return render_template('ajouter_user.html', error="Veuillez remplir tous les champs.")

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO utilisateurs (username, password, role) VALUES (?, ?, ?)',
                (username, password, role)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('ajouter_user.html', error="Nom d'utilisateur déjà utilisé.")
        conn.close()
        return redirect(url_for('liste_utilisateurs'))

    return render_template('ajouter_user.html', error=None)


@app.route('/supprimer_utilisateur/<int:user_id>', methods=['POST'])
def supprimer_utilisateur(user_id):
    if not est_authentifie() or not est_admin():
        return redirect(url_for('authentification'))

    # Empêcher un admin de se supprimer lui-même
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT username FROM utilisateurs WHERE id = ?', (user_id,))
    user = cursor.fetchone()

    if user and user[0] != 'admin':
        cursor.execute('DELETE FROM utilisateurs WHERE id = ?', (user_id,))
        conn.commit()

    conn.close()
    return redirect(url_for('liste_utilisateurs'))


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
    if not est_authentifie() or not est_admin():
        return redirect(url_for('authentification'))

    error = None

    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        prenom = request.form.get('prenom', '').strip()
        adresse = request.form.get('adresse', '').strip()

        if not nom or not prenom or not adresse:
            error = "Veuillez remplir tous les champs."
        else:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)',
                (nom, prenom, adresse)
            )
            conn.commit()
            conn.close()
            return redirect(url_for('enregistrer_client'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, created, nom, prenom, adresse FROM clients ORDER BY id DESC')
    clients = cursor.fetchall()
    conn.close()

    return render_template('ajouter_client.html', clients=clients, error=error)

@app.route('/supprimer_client/<int:client_id>', methods=['POST'])
def supprimer_client(client_id):
    if not est_authentifie() or not est_admin():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM clients WHERE id = ?', (client_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('enregistrer_client'))




# -----------------------------
# GESTION DES LIVRES
# -----------------------------

# Afficher tous les livres
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
        cursor.execute(
            'INSERT INTO livres (titre, auteur, stock) VALUES (?, ?, ?)',
            (titre, auteur, stock)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('lire_livres'))
    return render_template('ajouter_livre.html')

@app.route('/emprunts/')
def emprunts():
    if not est_authentifie():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT e.id,
               e.date_emprunt,
               e.date_retour,
               u.id, u.username, u.role,
               l.id, l.titre, l.auteur
        FROM emprunts e
        JOIN utilisateurs u ON u.id = e.utilisateur_id
        JOIN livres l ON l.id = e.livre_id
        ORDER BY e.id DESC
        LIMIT 200
    """)
    emprunts = cursor.fetchall()
    conn.close()

    return render_template('emprunts.html', emprunts=emprunts)

    
@app.route('/emprunter_livre/<int:livre_id>', methods=['GET', 'POST'])
def emprunter_livre_flow(livre_id):
    if not est_authentifie():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id, titre, auteur, stock FROM livres WHERE id = ?', (livre_id,))
    livre = cursor.fetchone()
    if not livre:
        conn.close()
        return "Livre introuvable", 404

    # Liste des utilisateurs (pas des clients)
    cursor.execute('SELECT id, username, role FROM utilisateurs ORDER BY username')
    utilisateurs = cursor.fetchall()

    error = None

    if request.method == 'POST':
        utilisateur_id = request.form.get('utilisateur_id')

        if not utilisateur_id:
            error = "Veuillez choisir un utilisateur."
        else:
            cursor.execute('SELECT stock FROM livres WHERE id = ?', (livre_id,))
            stock = cursor.fetchone()[0]

            if stock <= 0:
                error = "Stock insuffisant."
            else:
                cursor.execute(
                    'INSERT INTO emprunts (utilisateur_id, livre_id) VALUES (?, ?)',
                    (int(utilisateur_id), livre_id)
                )
                cursor.execute('UPDATE livres SET stock = stock - 1 WHERE id = ?', (livre_id,))
                conn.commit()
                conn.close()
                return redirect(url_for('emprunts'))

    conn.close()
    return render_template('emprunter_form.html', livre=livre, utilisateurs=utilisateurs, error=error)


@app.route('/retour_emprunt/<int:emprunt_id>', methods=['POST'])
def retour_emprunt(emprunt_id):
    if not est_authentifie():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT livre_id, date_retour FROM emprunts WHERE id = ?", (emprunt_id,))
    row = cursor.fetchone()

    if row:
        livre_id, date_retour = row
        if date_retour is None:
            cursor.execute(
                "UPDATE emprunts SET date_retour = CURRENT_TIMESTAMP WHERE id = ?",
                (emprunt_id,)
            )
            cursor.execute("UPDATE livres SET stock = stock + 1 WHERE id = ?", (livre_id,))
            conn.commit()

    conn.close()
    return redirect(url_for('emprunts'))



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
    due_date = request.form.get('due_date')  # YYYY-MM-DD ou None

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO tasks (title, description, status, due_date) VALUES (?, ?, ?, ?)',
        (title, description, status, due_date)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('tasks'))


@app.route('/supprimer_task/<int:task_id>', methods=['POST'])
def supprimer_task(task_id):
    if not est_authentifie():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('tasks'))


# -----------------------------
# RUN
# -----------------------------

if __name__ == "__main__":
    app.run(debug=True)
