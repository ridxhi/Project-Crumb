# 🧁 Project Crumb

A bakery management app I created using Python, Streamlit, and SQLite.

## About the Project

Project Crumb is a personal project I started because of my experience working at a cupcake bakery. While working there, I noticed how many things employees had to keep track of, like custom cake orders, pickup dates, and inventory.

I wanted to see if I could create a simple application that would help organize these tasks in one place.

I'm still learning programming, so this project was also a way for me to practice Python, work with databases, and get experience building an application outside of class.

This is an independent project and isn't connected to any actual bakery.

## Features

Here are some of the features I included:

- **Dashboard:** Shows cake requests, order statuses, upcoming pickups, and low-stock ingredients.
- **Cake Requests:** Employees can enter custom cake orders with customer details, pickup dates, and special instructions.
- **Baker View:** Bakers can review orders, approve or decline them, request changes, and leave notes.
- **Owner View:** Allows the owner to manage inventory and archive or restore orders.
- **Inventory:** Keeps track of ingredients and lets users update quantities.
- **Search and Filters:** Makes it easier to find orders by customer name or status.
- **Database:** Uses SQLite to save information so it doesn't disappear when the application is closed.
- **Sample Data:** Includes fictional orders to test out the application.

## How to Run the Project

You'll need Python 3.10 or newer installed on your computer.

**1. Create a virtual environment:**

```bash
python -m venv .venv
```

**2. Activate it:**

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Mac/Linux:

```bash
source .venv/bin/activate
```

**3. Install the required packages:**

```bash
pip install -r requirements.txt
```

**4. Start the application:**

```bash
streamlit run app.py
```

Once the app starts, Streamlit will give you a local link, usually http://localhost:8501.

You can switch between Employee, Baker, and Owner views using the sidebar. There's also an option to load sample data if you want to try out the features.

## Testing

I included a few basic tests to check that the database functions work correctly.

To run them:

```bash
python -m unittest discover -s tests -v
```

## Tools I Used

- **Python:** For the main application and its functions.
- **Streamlit:** To create the interface and dashboard.
- **SQLite:** To store cake orders and inventory information.
- **unittest:** To test some of the database functions.

## Things to Know

This is a beginner portfolio project that I created for learning and practice. It's not meant to be used by an actual bakery yet.

The different employee roles are just demo views and don't have real login security. The app also doesn't process payments or accept online orders.

Since the database is stored locally, this version is mainly meant to run on a computer rather than as a full online service. Any customer information used for testing should be fictional.

## What I'd Like to Add Later

As I learn more, I'd like to improve the project by adding:

- Actual employee login accounts.
- A cloud database so information can be accessed from different devices.
- Notifications when a cake order is approved or updated.
- More detailed inventory tracking.

## Why I Made This

I wanted to build something based on a problem I had actually seen while working.

Working at a bakery gave me an idea of how much organization goes into managing orders and keeping track of ingredients. I thought it would be interesting to use what I've been learning in computer science to create something that could make those tasks easier.

Project Crumb helped me get more practice with Python and learn how different parts of an application work together. It's also something I can continue improving as I gain more programming experience.