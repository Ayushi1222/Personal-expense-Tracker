# 💰 Personal Finance Tracker API with Budget Monitoring & Smart Alerts

## 📌 Overview
The **Personal Finance Tracker API** helps users take control of their finances by allowing them to record incomes, expenses, and set monthly budgets for different categories. It provides smart alerts when budget limits are reached, along with detailed monthly reports. Built with **FastAPI**, **SQLAlchemy ORM**, and **Snowflake** database, it offers a secure and scalable financial management backend.

---

## ✨ Features
- **User Management**: Create, read, update, and delete user accounts (passwords stored securely in hashed form).
- **Expense Categories**: Add and manage categories such as Food, Rent, Entertainment, etc.
- **Transactions**: Record income/expense transactions with date, amount, and description.
- **Budgets & Alerts**: Set monthly budgets per category and get alerts at 80%, 90%, and 100% usage.
- **Reports**: Generate monthly summaries and category-wise spending insights.
- **Advanced Filters**: Search/filter transactions by date, category, and type.
- **Pagination**: Efficient browsing of large transaction lists.
- **API Documentation**: Interactive Swagger/OpenAPI UI (provided by FastAPI).

---

## 🛠 Tech Stack
- **Language**: Python 3.9+
- **Framework**: FastAPI
- **Database**: Snowflake
- **ORM**: SQLAlchemy
- **Authentication**: JWT
- **Hashing**: bcrypt
- **Environment**: venv

---

## 📂 Database Schema

**Users Table**
- `id` (PK)
- `username` (unique)
- `email`
- `password` (hashed)

**Expense Categories**
- `id`
- `name`
- `user_id` (FK)

**Transactions**
- `id`
- `amount`
- `description`
- `type` (income/expense)
- `category_id` (FK)
- `user_id` (FK)
- `transaction_date`

**Budgets**
- `id`
- `user_id`
- `category_id`
- `month` (YYYY-MM)
- `budget_amount`

---

## 🚀 Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/personal-finance-tracker.git
cd personal-finance-tracker
```

### 2️⃣ Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables
Create a `.env` file in the root directory with:
```env
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema
SNOWFLAKE_WAREHOUSE=your_warehouse
JWT_SECRET=your_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 5️⃣ Run the Application
```bash
uvicorn main:app --reload
```

The application will be available at `http://127.0.0.1:8000`

---

## 🔧 API Endpoints

### **Default**
- `GET /` - Read Root

### **Authentication**
- `POST /auth/register` - Register User
- `POST /auth/login` - Login User

### **Users**
- `GET /users/` - Read Users
- `GET /users/me` - Get Me
- `GET /users/{user_id}` - Read User

### **Categories**
- `GET /categories` - Get Categories
- `POST /categories` - Add Category
- `PUT /categories/{category_id}` - Edit Category
- `DELETE /categories/{category_id}` - Remove Category

### **Expenses**
- `GET /expenses` - Get Expenses
- `POST /expenses` - Add Expense
- `DELETE /expenses/{expense_id}` - Remove Expense
- `GET /expenses/summary/{month}` - Get Monthly Summary
- `GET /expenses/summary-by-category/{month}` - Get Monthly Summary By Category

### **Budgets**
- `GET /budgets/` - Read All Budgets
- `POST /budgets/` - Add Budget
- `PUT /budgets/{budget_id}` - Edit Budget
- `DELETE /budgets/{budget_id}` - Remove Budget
- `GET /budgets/{month}` - Read Budget

---

## 📋 Dependencies (requirements.txt)
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
snowflake-sqlalchemy==1.5.0
snowflake-connector-python==3.5.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
pydantic==2.5.0
alembic==1.13.0
```

---

## 🧪 Testing
```bash
pytest
```

---
