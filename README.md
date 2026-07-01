# todo-fullstack

API REST de gestión de tareas (backend) + interfaz web (frontend), desarrollado como Trabajo Práctico de Ingeniería de Software III — FCEQyN, UNaM.

**Autor:** Leandro Lobayan

---

## Estructura del repositorio

```
todo-fullstack/
├── backend/          # API REST en Flask + SQLite
│   ├── app/
│   ├── tests/
│   ├── requirements.txt
│   ├── Procfile       # Indica a Render cómo correr la app
│   └── run.py
├── frontend/          # UI estática en HTML/CSS/JS vanilla
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── netlify.toml
└── sonar-project.properties
```

---

## Deploy del backend en Render

1. Crear cuenta en [render.com](https://render.com) (se recomienda vincular con GitHub).
2. **New** → **Web Service** → seleccionar este repositorio.
3. Configuración:
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app`
4. Click en **Create Web Service**. Render asigna una URL pública del tipo `https://nombre-servicio.onrender.com`.

## Deploy del frontend en Netlify

1. Crear cuenta en [netlify.com](https://netlify.com) (se recomienda vincular con GitHub).
2. **Add new site** → **Import an existing project** → seleccionar este repositorio.
3. Configuración:
   - **Base directory:** `frontend`
   - **Build command:** (vacío, no requiere build)
   - **Publish directory:** `frontend`
4. Antes de deployar, editar `frontend/script.js` y reemplazar `API_URL` con la URL real del backend en Render.
5. Click en **Deploy site**.

---

## Desarrollo local

### Backend
```bash
cd backend
pip install -r requirements.txt
python run.py
```
Corre en `http://localhost:5000`.

### Frontend
Abrir `frontend/index.html` directamente en el navegador, o servir con:
```bash
cd frontend
python -m http.server 8080
```
Corre en `http://localhost:8080`.
