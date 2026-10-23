from flask import (Flask, abort, flash, jsonify, redirect,
                   render_template, request, session, url_for)

app = Flask(__name__)
# Clé secrète : indispensable pour signer le cookie de session et pour flash().
# Générée avec : python -c "import secrets; print(secrets.token_hex())"
# (en vrai projet : à lire dans une variable d'environnement, jamais dans Git)
app.secret_key = "c3f1a9d27e5b40a8b6d1f0e94c2a7b835d6e1f90a4b2c7d83e5f60718293a4b5"

PRIORITES = ("basse", "normale", "haute")
FILTRES = ("toutes", "actives", "terminees")

taches = [
    {"id": 1, "titre": "Réviser les décorateurs",
     "priorite": "haute", "terminee": False},
    {"id": 2, "titre": "Installer Flask",
     "priorite": "normale", "terminee": True},
    {"id": 3, "titre": "Lire la doc Jinja2",
     "priorite": "basse", "terminee": False},
]


def trouver(id):
    """Renvoie la tâche d'identifiant `id`, ou déclenche une vraie erreur 404."""
    for t in taches:
        if t["id"] == id:
            return t
    abort(404)


# ---------- Missions 1, 3 et 6 : accueil, liste, filtre mémorisé ----------
@app.route("/")
def index():
    # Le paramètre d'URL gagne ; sinon on reprend le dernier filtre de la session.
    filtre = request.args.get("filtre") or session.get("filtre", "toutes")
    if filtre not in FILTRES:          # ne jamais faire confiance à l'URL
        filtre = "toutes"
    session["filtre"] = filtre

    if filtre == "actives":
        visibles = [t for t in taches if not t["terminee"]]
    elif filtre == "terminees":
        visibles = [t for t in taches if t["terminee"]]
    else:
        visibles = taches

    restantes = sum(1 for t in taches if not t["terminee"])
    return render_template("taches.html", taches=visibles,
                           restantes=restantes, filtre=filtre)


# ---------- Mission 2 : route dynamique avec convertisseur int ----------
@app.route("/taches/<int:id>")
def tache(id):
    return render_template("tache.html", tache=trouver(id))


# ---------- Mission 5 : formulaire, validation, POST/redirect/GET ----------
@app.route("/taches/ajouter", methods=["GET", "POST"])
def ajouter():
    if request.method == "POST":
        titre = request.form.get("titre", "").strip()
        priorite = request.form.get("priorite", "normale")

        erreurs = []
        if not titre:
            erreurs.append("Le titre est obligatoire.")
        elif len(titre) > 80:
            erreurs.append("Le titre ne doit pas dépasser 80 caractères.")
        if priorite not in PRIORITES:
            erreurs.append("Priorité invalide.")

        if erreurs:
            # On réaffiche le formulaire (code 400) en gardant la saisie.
            return render_template("ajouter.html", erreurs=erreurs,
                                   titre=titre, priorite=priorite), 400

        nouvel_id = max((t["id"] for t in taches), default=0) + 1
        taches.append({"id": nouvel_id, "titre": titre,
                       "priorite": priorite, "terminee": False})
        flash("Tâche ajoutée")                       # Mission 6
        return redirect(url_for("index"))            # Mission 5 : PRG
    return render_template("ajouter.html", erreurs=[], titre="",
                           priorite="normale")


# ---------- Bonus 1 : actions en POST uniquement ----------
@app.post("/taches/<int:id>/terminer")
def terminer(id):
    t = trouver(id)
    t["terminee"] = True
    flash("Tâche terminée")
    return redirect(url_for("index"))


@app.post("/taches/<int:id>/supprimer")
def supprimer(id):
    taches.remove(trouver(id))
    flash("Tâche supprimée")
    return redirect(url_for("index"))


# ---------- Bonus 2 : page 404 personnalisée (avec le code 404) ----------
@app.errorhandler(404)
def page_introuvable(e):
    return render_template("404.html"), 404


# ---------- Bonus 3 : API JSON ----------
@app.route("/api/taches")
def api_taches():
    return jsonify(taches)   # Content-Type: application/json


if __name__ == "__main__":
    app.run(debug=True)
