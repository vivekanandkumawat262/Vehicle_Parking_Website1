# 🚗 Vehicle Parking Management System (Flask Backend)

This is the backend API for the **Vehicle Parking Website**, developed using **Flask**, **SQLAlchemy**, and **SQLite3**.  
It allows users to register, log in, and manage parking-related information within different cities and car parks.

---

## 📅 Today's Progress (27 Oct 2025)

### ✅ Project Setup
- Initialized Flask backend with proper folder structure.
- Configured virtual environment (`.env`) and installed dependencies.
- Created SQLite database file: `secureDb.sqlite3`.
- Integrated **SQLAlchemy ORM** for database models.
- Added **CORS** and **JWT Authentication** setup.

---

## 🧱 Database Models Created

### **User**
- Fields: `first_name`, `last_name`, `email`, `vehicle_reg_number`, `postcode`, `phone_number`, `gender`, `age`, etc.
- Relationships:
  - Belongs to one **City**
  - Can access multiple **Car Parks**

### **City**
- Represents a city that contains car parks.
- Fields: `id`, `name`

### **CarPark**
- Represents parking lots within a city.
- Fields: `id`, `name`, `city_id`

### **user_carparks (Association Table)**
- Handles the **many-to-many relationship** between users and car parks.

---

## ⚙️ API Routes Implemented

### 1️⃣ **City Management**

#### ➕ Add City
**POST** `/cities`
```json
{
  "name": "Chennai"
}






📋 Get All Cities

GET /cities

2️⃣ Car Park Management
➕ Add Car Parks Under a City

POST /create_carparks

{
  "carparks": [
    {"name": "Central Mall Parking", "city_id": 1},
    {"name": "Phoenix Market City", "city_id": 1}
  ]
}

📋 Get Cities With Car Parks

GET /get_cities_with_carparks

3️⃣ User Authentication
🧍‍♂️ Sign Up

POST /signup

{
  "first_name": "Vivekanand",
  "last_name": "Kumawat",
  "email": "vivekanand@gmail.com",
  "confirm_email": "vivekanand@gmail.com",
  "vehicle_reg_number": "RJ23AB1234",
  "postcode": "332001",
  "phone_number": "9876543210",
  "preferred_mode": "Email & SMS",
  "password": "12345",
  "confirm_password": "12345",
  "gender": "Male",
  "age": 21,
  "city_id": 1,
  "carpark_ids": [1, 2]
}

🔐 Login

POST /login

{
  "email": "vivekanand@gmail.com",
  "password": "12345"
}


Response:

{
  "message": "Login successful",
  "token": "JWT_ACCESS_TOKEN",
  "user": {
    "id": 1,
    "email": "vivekanand@gmail.com",
    "name": "Vivekanand"
  }
}

🧪 Testing with Postman

Open Postman.

Use the above endpoints to:

Add cities and car parks.

Create new users.

Log in and verify JWT authentication.

Use GET routes to confirm database data.

🛠️ Tech Stack

Backend: Flask

Database: SQLite3

ORM: SQLAlchemy

Auth: Flask-JWT-Extended

CORS: flask-cors

Testing: Postman

👨‍💻 Author

Vivekanand Kumawat
IIT Madras BS Degree Student in Data Science
Backend Developer | Flask | Python | SQLAlchemy

🚀 Next Steps

Add user dashboard routes.

Implement vehicle parking booking logic.

Connect backend with frontend UI.