# 🍽️ TheKnife - Restaurant Reservation System

A full-stack restaurant reservation management system built with Flask and MySQL. Features include restaurant browsing with allergen filtering, client management, reservations, invoicing, and reviews. The application supports Michelin-starred restaurants across Spain with detailed dish menus and allergen information for dietary requirements.

## Features
- Restaurant search and filtering by allergens
- Client registration and management
- Reservation system with date and time selection
- Invoice generation and management
- Reviews and ratings for restaurants
- Data visualization with Matplotlib

## Tech Stack
- **Backend:** Python, Flask, Flask-MySQLdb
- **Database:** MySQL (`theknife_db`)
- **Frontend:** HTML, CSS, JavaScript
- **Data Visualization:** Matplotlib

## Project Structure
```
BaseDeDatos/           # Raw CSV data and SQL scripts
proyecto_final/        # Main application code and scripts
  ├── databases_csv/   # Processed CSVs and table generators
  ├── files_test_build/# Test scripts and configs
  └── src/             # Flask app, static, and templates
```

## Getting Started
1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Entrega_Proyecto_Final_G3.git
   cd Entrega_Proyecto_Final_G3
   ```
2. **Set up a Python virtual environment:**
   ```bash
   python3 -m venv env
   source env/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up the MySQL database:**
   - Run the SQL scripts in `BaseDeDatos/` to create and populate the database.
   - Update your database credentials in `src/config.py`.
5. **Run the Flask app:**
   ```bash
   cd proyecto_final/src
   flask run
   ```

## License
This project is for educational purposes.

---

**Authors:** Daniel Aguilera, Claudia Agromayor, Álvaro Gracia, Jose Manuel Guinea
