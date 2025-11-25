# Guide d'Utilisation du Système de Mise à Jour

## Vue d'ensemble

L'application Espoofer inclut maintenant un système de mise à jour automatique qui permet de :
- Vérifier automatiquement les nouvelles versions au démarrage
- Télécharger et installer les mises à jour en un clic
- Vérifier manuellement les mises à jour via le menu

## Pour les Utilisateurs

### Vérification automatique

L'application vérifie automatiquement les mises à jour au démarrage. Si une nouvelle version est disponible, une notification s'affiche.

### Vérification manuelle

1. Ouvrez l'application
2. Cliquez sur le menu **"Aide"** dans la barre de menu
3. Sélectionnez **"Vérifier les mises à jour"**

### Installation d'une mise à jour

Lorsqu'une mise à jour est disponible :

1. Une boîte de dialogue s'affiche avec les informations de la nouvelle version
2. Cliquez sur **"Oui"** pour télécharger et installer
3. Une barre de progression affiche l'avancement du téléchargement
4. L'application redémarre automatiquement après l'installation

## Pour les Développeurs

### Structure des fichiers

```
espoofer/
├── version.py          # Version actuelle de l'application
├── updater.py          # Module de mise à jour
├── build.py            # Script de build
├── update_info.json    # Informations de mise à jour (sur le serveur)
└── BUILD_INSTRUCTIONS.md  # Instructions détaillées
```

### Workflow de release

1. **Mettre à jour la version** dans `version.py`
2. **Construire l'exécutable** avec `python build.py`
3. **Créer un release** sur GitHub avec le fichier ZIP
4. **Mettre à jour** `update_info.json` avec les nouvelles informations
5. **Publier** le release

### Configuration de l'URL de mise à jour

Par défaut, l'URL pointe vers :
```
https://raw.githubusercontent.com/votre-repo/espoofer/main/update_info.json
```

Pour changer cette URL, modifiez la ligne dans `updater.py` :
```python
self.update_url = update_url or "VOTRE_URL_ICI"
```

### Format de update_info.json

```json
{
  "version": "1.0.1",
  "release_date": "2024-01-15",
  "changelog": "- Correction de bugs\n- Nouvelles fonctionnalités",
  "download_url": "https://github.com/votre-repo/espoofer/releases/download/v1.0.1/Espoofer_v1.0.1_windows.zip",
  "size": "~5 MB"
}
```

## Dépannage

### L'application ne détecte pas les mises à jour

1. Vérifiez votre connexion Internet
2. Vérifiez que `update_info.json` est accessible publiquement
3. Vérifiez que la version dans `update_info.json` est supérieure à la version actuelle

### Erreur lors du téléchargement

1. Vérifiez que l'URL de téléchargement est correcte
2. Vérifiez que le fichier existe sur le serveur
3. Vérifiez les permissions d'écriture dans le répertoire temporaire

### L'application ne redémarre pas après la mise à jour

1. Fermez manuellement l'application
2. Relancez-la - la nouvelle version devrait être installée
3. Si le problème persiste, téléchargez manuellement depuis le site

## Sécurité

- Les téléchargements utilisent HTTPS (recommandé)
- Les fichiers sont vérifiés avant l'installation
- Un backup est créé avant la mise à jour (optionnel)

## Support

Pour toute question ou problème, consultez le fichier `BUILD_INSTRUCTIONS.md` ou ouvrez une issue sur GitHub.

