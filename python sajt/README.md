````markdown
# IT Help Desk / Ticket System

A web-based IT Help Desk and Ticket Management System built with Python, Flask and SQLite.

The application allows users to register, log in, create IT support tickets, manage their profile and track the status of their reported problems.

Administrators have additional permissions for managing users and support tickets.

---

## 🚀 Features

### User Management

- User registration
- User login and logout
- Password hashing
- Password confirmation
- Password change
- Profile page
- Session-based authentication
- Email uniqueness validation

### Ticket Management

Users can create support tickets with:

- Title
- Description
- Category
- Priority

Available categories:

- Hardware
- Software
- Network
- Account
- Other

Available priorities:

- Low
- Medium
- High
- Critical

Available ticket statuses:

- Open
- In Progress
- Resolved
- Closed

Users can also view their submitted tickets and their current status.

---

## 👨‍💻 Admin Panel

Administrators can:

- View system statistics
- View registered users
- Edit users
- Delete users
- Grant or remove administrator permissions
- View all support tickets
- Change ticket status
- Delete tickets
- View ticket information
- Monitor critical tickets

---

## 📊 Dashboard

The user dashboard provides information about:

- Total tickets
- Open tickets
- Tickets in progress
- Resolved tickets
- Critical tickets
- Recent tickets

The administrator dashboard provides an overview of:

- Total users
- Total administrators
- Total tickets
- Open tickets
- Tickets in progress
- Resolved tickets
- Critical tickets

---

## 🖥️ System Information

The application also displays basic system information such as:

- Hostname
- IP address
- Operating system
- Operating system version
- Python version
- Flask version

---

## 🔐 Security

The application includes several basic security features:

- Password hashing using Werkzeug
- Session-based authentication
- Protected admin routes
- User authorization checks
- Password validation
- Email validation
- Environment variables for the Flask secret key
- `.gitignore` protection for sensitive files
- Input validation
- Database queries using parameters

---

## 🛠️ Technologies

- Python
- Flask
- SQLite
- HTML5
- CSS3
- Jinja2
- Werkzeug
- python-dotenv

---

## 📁 Project Structure

```text
IT-Help-Desk/
│
├── app1.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── change_password.html
│   ├── create_ticket.html
│   ├── my_tickets.html
│   ├── admin.html
│   ├── admin_tickets.html
│   ├── edit_user.html
│   └── system_info.html
│
├── static/
│   └── style.css
│
├── .env
└── database.db
````

`.env` and `database.db` should not be uploaded to GitHub.

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Enter the project directory

```bash
cd IT-Help-Desk
```

### 3. Create a virtual environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

---

## 📦 Install dependencies

```powershell
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```text
SECRET_KEY=your-secret-key
```

Do not upload the `.env` file to GitHub.

---

## ▶️ Run the Application

Run:

```powershell
python app1.py
```

The application will start on:

```text
http://127.0.0.1:5000
```

Open the address in your browser.

---

## 🗄️ Database

The project uses SQLite.

The database is automatically created when the application starts.

The database contains tables for:

* Users
* Tickets

The local database file is intentionally excluded from GitHub using `.gitignore`.

---

## 🎯 Project Purpose

This project was created as a practical Python/Flask project for learning and demonstrating:

* Web application development
* Python programming
* Flask
* SQL and SQLite
* Authentication
* Authorization
* Password hashing
* CRUD operations
* Database relationships
* Session management
* Basic application security
* IT Help Desk concepts

---

## 🔮 Future Improvements

Possible future improvements include:

* CSRF protection
* Ticket comments
* Ticket search
* Ticket filtering
* File attachments
* Email notifications
* Password reset by email
* Advanced administrator statistics
* Docker support
* Automated testing
* CI/CD with GitHub Actions

---

## 👤 Author

Developed as a personal Python and IT Help Desk portfolio project.

---

## 📄 License

This project is intended for educational and portfolio purposes.

```
```
