@echo off
chcp 65001 >nul
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║          🧪 TEST DU SERVICE ML - PRÉDICTIONS D'ACHAT             ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

REM Vérifier si l'environnement virtuel existe
if not exist "venv\" (
    echo ❌ Environnement virtuel non trouvé
    echo.
    echo 💡 Créer l'environnement virtuel d'abord :
    echo    python -m venv venv
    echo    venv\Scripts\activate
    echo    pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Activer l'environnement virtuel
echo 🔄 Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Vérifier si les dépendances sont installées
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo ❌ Dépendances non installées
    echo.
    echo 💡 Installer les dépendances :
    echo    pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Créer les dossiers si nécessaire
if not exist "models\" mkdir models
if not exist "logs\" mkdir logs

REM Copier .env.example si .env n'existe pas
if not exist ".env" (
    if exist ".env.example" (
        echo 📝 Création du fichier .env...
        copy .env.example .env >nul
    )
)

echo.
echo ✅ Environnement prêt
echo.
echo ════════════════════════════════════════════════════════════════════
echo.

REM Lancer les tests
python test_simple.py

echo.
echo ════════════════════════════════════════════════════════════════════
echo.
echo 💡 Pour démarrer le service ML :
echo    python -m app.main
echo.
echo 💡 Pour accéder à la documentation :
echo    http://localhost:8000/api/v1/docs
echo.
pause
