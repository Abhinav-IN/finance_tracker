# 📊 Finance Tracker (FastAPI)

A simple FastAPI backend to serve APIs for a finance tracking application.

---

## 📁 Project Structure

```
finance_tracker/
│── backend/
│   ├── server.py         # Main FastAPI server
│   ├── routes/
│   │   ├── __init__.py   # Required for package imports
│   │   ├── user.py       # User-related API routes
│   ├── models/           # Database models (empty for now)
│── static/
│   ├── index.html        # Static frontend files
│── .venv/                # Virtual environment (generated)
│── README.md             # Project documentation
```

---

## 🛠 Installation & Setup

### 1️⃣ Clone the Repository

```sh
git clone https://github.com/your-username/finance_tracker.git
cd finance_tracker
```

### 2️⃣ Set Up a Virtual Environment

```sh
python -m venv .venv
```

#### Activate the Virtual Environment

- **Windows:**
  ```sh
  .venv\Scripts\activate
  ```
- **Linux/macOS:**
  ```sh
  source .venv/bin/activate
  ```

### 3️⃣ Install Dependencies

```sh
pip install fastapi uvicorn
```

---

## 🚀 Running the Server

Run the following command to start the server:

```sh
uvicorn api.server:app --reload
```

The server will start at:

- 📂 **Static Files:** `http://127.0.0.1:8000/`
- 🌐 **Base API URL:** `http://127.0.0.1:8000/api`
- 👤 **User Profile API:** `http://127.0.0.1:8000/users/profile`

---

## 📌 API Endpoints

| Method | Endpoint         | Description        |
| ------ | ---------------- | ------------------ |
| `GET`  | `/`              | Root API status    |
| `GET`  | `/users/profile` | Fetch user profile |

---

## 💡 Next Steps

- 🔑 Add authentication (`/auth/login`, `/auth/register`)
- 🗄️ Set up a database (`SQLite`, `PostgreSQL`, or `MongoDB`)
- 🎨 Build a frontend and integrate with the backend

---
