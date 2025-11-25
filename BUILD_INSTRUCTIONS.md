# Instructions de Build et Distribution

Ce guide explique comment créer une application téléchargeable avec système de mise à jour automatique.

## Prérequis

1. Python 3.7 ou supérieur
2. PyInstaller : `pip install pyinstaller`
3. Toutes les dépendances du projet

## Structure des fichiers

- `version.py` : Gère la version de l'application
- `updater.py` : Système de mise à jour automatique
- `build.py` : Script de build pour créer l'exécutable
- `update_info.json` : Fichier JSON contenant les informations de mise à jour

## Étapes de Build

### 1. Préparer la version

Modifiez `version.py` pour définir la nouvelle version :
```python
__version__ = "1.0.1"
```

### 2. Construire l'exécutable

Exécutez le script de build :
```bash
python build.py
```

Cela va :
- Créer un exécutable dans le dossier `dist/`
- Créer un package ZIP pour la distribution

### 3. Configurer le serveur de mise à jour

#### Option A : Utiliser GitHub Releases (Recommandé)

1. Créez un nouveau release sur GitHub avec la version (ex: v1.0.1)
2. Uploadez le fichier ZIP créé dans `dist/`
3. Modifiez `update_info.json` dans votre dépôt avec :
   - La nouvelle version
   - L'URL de téléchargement du release GitHub
   - Le changelog

Exemple d'URL GitHub :
```
https://github.com/votre-username/espoofer/releases/download/v1.0.1/Espoofer_v1.0.1_windows.zip
```

4. Assurez-vous que `update_info.json` est accessible publiquement :
   - Soit dans le dépôt principal
   - Soit via GitHub Pages ou Raw GitHub

#### Option B : Utiliser votre propre serveur

1. Uploadez le fichier ZIP sur votre serveur
2. Créez un fichier `update_info.json` accessible via HTTP/HTTPS
3. Configurez l'URL dans `updater.py` ou via un paramètre

### 4. Mettre à jour update_info.json

Modifiez `update_info.json` avec les bonnes informations :

```json
{
  "version": "1.0.1",
  "release_date": "2024-01-15",
  "changelog": "- Correction de bugs\n- Nouvelles fonctionnalités",
  "download_url": "https://github.com/votre-repo/espoofer/releases/download/v1.0.1/Espoofer_v1.0.1_windows.zip",
  "size": "~5 MB"
}
```

### 5. Tester la mise à jour

1. Installez une ancienne version de l'application
2. Lancez l'application
3. Vérifiez que la mise à jour est détectée
4. Testez le téléchargement et l'installation

## Configuration de l'URL de mise à jour

Par défaut, l'URL de mise à jour pointe vers :
```
https://raw.githubusercontent.com/votre-repo/espoofer/main/update_info.json
```

Pour changer cette URL, modifiez la ligne dans `updater.py` :
```python
self.update_url = update_url or "VOTRE_URL_ICI"
```

Ou passez l'URL lors de l'initialisation :
```python
updater = Updater(update_url="https://votre-serveur.com/update_info.json")
```

## Distribution

### Pour Windows

1. Build avec `python build.py`
2. Le fichier `Espoofer.exe` sera dans `dist/`
3. Créez un installer avec Inno Setup ou NSIS (optionnel)
4. Uploadez sur GitHub Releases ou votre serveur

### Pour Linux

1. Build avec `python build.py`
2. Le fichier `Espoofer` sera dans `dist/`
3. Créez un package .deb ou .rpm (optionnel)
4. Uploadez sur GitHub Releases ou votre serveur

### Pour macOS

1. Build avec `python build.py`
2. Le fichier `Espoofer` sera dans `dist/`
3. Créez un .dmg (optionnel)
4. Uploadez sur GitHub Releases ou votre serveur

## Sécurité

Pour une production, considérez :

1. **Signature des fichiers** : Signez vos exécutables avec un certificat de code
2. **Vérification de checksum** : Implémentez la vérification MD5/SHA256 dans `updater.py`
3. **HTTPS** : Utilisez toujours HTTPS pour les téléchargements
4. **Authentification** : Ajoutez une authentification pour protéger votre serveur de mise à jour

## Automatisation avec GitHub Actions

Créez `.github/workflows/build.yml` :

```yaml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, ubuntu-latest, macos-latest]
    
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pyinstaller
      - name: Build
        run: python build.py
      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: ${{ matrix.os }}
          path: dist/
```

## Notes importantes

- Les mises à jour sont vérifiées automatiquement au démarrage
- L'utilisateur peut vérifier manuellement via le menu "Aide > Vérifier les mises à jour"
- Les mises à jour nécessitent un redémarrage de l'application
- Un backup est créé avant l'installation (optionnel)

