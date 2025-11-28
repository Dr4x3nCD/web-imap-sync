# Web IMAP Sync | Ultimate Migration Tool

[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://hub.docker.com/r/levide229/mail_migration_tool)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📋 Description

**Web IMAP Sync** est une application web moderne et intuitive pour la migration d'emails entre serveurs IMAP. Basée sur l'outil robuste `imapsync`, elle offre une interface utilisateur premium avec des fonctionnalités avancées pour simplifier les migrations d'emails.

### ✨ Fonctionnalités Principales

- 🎯 **Interface Moderne** : Design premium avec Bootstrap 5 et animations fluides
- 🔐 **Test de Connexion Intelligent** : Validation indépendante de chaque serveur avec feedback détaillé
- 🚀 **Auto-détection IMAP** : Détection automatique des paramètres pour Gmail, Office365, Yahoo, etc.
- 👁️ **Visibilité des Mots de Passe** : Icône œil pour afficher/masquer les mots de passe
- 📋 **Messages Copiables** : Modal personnalisé avec copie dans le presse-papiers
- 🔄 **Mode Batch** : Migration de plusieurs comptes via fichier CSV
- 👻 **Mode Arrière-plan** : Lancement de tâches en arrière-plan avec suivi via code secret
- 📊 **Suivi en Temps Réel** : Logs de migration en streaming
- 🛠️ **Configuration Avancée** : Support complet des options imapsync (filtres, préfixes, OAuth, etc.)
- 🎨 **Aperçu de Commande** : Visualisation de la commande imapsync générée

## 🚀 Démarrage Rapide

### Option 1 : Docker Hub (Recommandé)

```bash
# Télécharger l'image
docker pull levide229/mail_migration_tool:latest

# Lancer le conteneur
docker run -d -p 5000:5000 --name web-imap-sync levide229/mail_migration_tool:latest
```

### Option 2 : Build Local

```bash
# Cloner le dépôt
git clone https://github.com/Dr4x3nCD/web-imap-sync.git
cd web-imap-sync

# Construire l'image
docker build -t web-imap-sync .

# Lancer le conteneur
docker run -d -p 5000:5000 --name web-imap-sync web-imap-sync
```

### Option 3 : Développement Local

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python app.py
```

## 📖 Utilisation

1. **Accéder à l'interface** : Ouvrez `http://localhost:5000` dans votre navigateur

2. **Configurer la connexion** :
   - Remplissez les informations du serveur source (Host1)
   - Remplissez les informations du serveur destination (Host2)
   - Utilisez l'auto-détection en laissant le champ "Host" vide

3. **Tester la connexion** :
   - Cliquez sur "Tester la connexion"
   - Vérifiez que les deux serveurs sont accessibles
   - Les erreurs sont maintenant copiables pour faciliter le débogage

4. **Configurer les options** (optionnel) :
   - **Dossiers** : Filtres, préfixes, mapping
   - **Filtres & Règles** : Age, taille, recherche IMAP
   - **Performance** : Limitation de vitesse, cache
   - **Avancé** : Timeouts, labels, ACLs
   - **Zone Danger** : Suppressions (attention !)

5. **Lancer la migration** :
   - Mode normal : Suivi en temps réel
   - Mode arrière-plan : Récupération via code secret

## 🎨 Captures d'Écran

L'interface propose :
- Design moderne avec glassmorphism
- Onglets organisés par catégorie
- Tooltips informatifs sur chaque champ
- Prévisualisation de la commande imapsync
- Modal personnalisé pour les messages d'erreur

## 🔧 Configuration Avancée

### Variables d'Environnement

```bash
# Secret key pour les sessions (recommandé en production)
FLASK_SECRET_KEY=your-secret-key-here

# Dossier de téléchargement
UPLOAD_FOLDER=/tmp/imapsync_uploads
```

### Pré-configurations Disponibles

- Gmail ➔ Gmail
- Office 365 ➔ Office 365
- Exchange ➔ Exchange
- Gmail ➔ Office 365

## 🐛 Dépannage

### Erreur d'authentification

Si vous obtenez une erreur d'authentification :
1. Vérifiez vos identifiants dans le webmail
2. Vérifiez si vous utilisez un mot de passe d'application
3. Utilisez le test de connexion pour identifier quel serveur échoue
4. Copiez le message d'erreur pour analyse

### Problème de préfixes

Si aucun dossier n'est synchronisé :
- Vérifiez les préfixes suggérés dans les logs
- Utilisez l'onglet "Dossiers" pour configurer les préfixes
- Consultez l'analyse automatique des erreurs

## 📦 Structure du Projet

```
web-imap-sync/
├── app.py                 # Application Flask principale
├── templates/
│   ├── index.html        # Interface principale
│   ├── results.html      # Page de résultats
│   ├── track.html        # Suivi de tâche
│   └── task_started.html # Confirmation mode arrière-plan
├── static/
│   └── style.css         # Styles personnalisés
├── Dockerfile            # Configuration Docker
├── requirements.txt      # Dépendances Python
└── imapsync             # Binaire imapsync
```

## 🛠️ Technologies Utilisées

- **Backend** : Flask (Python 3.9+)
- **Frontend** : Bootstrap 5, Font Awesome, JavaScript ES6
- **Migration** : imapsync (Perl)
- **Conteneurisation** : Docker

## 📝 Prérequis

- **Docker** : Pour le déploiement conteneurisé
- **Python 3.9+** : Pour l'exécution locale
- **Perl et modules** : Requis par imapsync (inclus dans Docker)

## 🤝 Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à :
- Ouvrir une issue pour signaler un bug
- Proposer une pull request pour une amélioration
- Suggérer de nouvelles fonctionnalités

## 📄 Licence

Ce projet est sous licence MIT. Vous êtes libre de l'utiliser, le modifier et le distribuer.

## 🙏 Remerciements

- [imapsync](https://imapsync.lamiral.info/) par Gilles LAMIRAL
- [Bootstrap](https://getbootstrap.com/)
- [Font Awesome](https://fontawesome.com/)

## 📞 Support

Pour toute question ou problème :
- Ouvrez une issue sur GitHub
- Consultez la documentation d'imapsync
- Utilisez la fonction "Copier le message" pour partager les erreurs

---

**Fait avec ❤️ pour simplifier les migrations d'emails**
