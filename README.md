# Money Mantra
A web app for tracking expenses and budgets.

## Features
  * Quick and bulk expensing
  * Budget creation and automatic tracking of expenses per budget
  * Custom spend categories
  * Dashboard with dynamic reporting
  * Detailed reports that break down spending
  * Add additional payers for tracking expenses across multiple people
  * Export your data directly into raw, CSV, and Excel
  * Responsive design - compatible with all major browsers and devices

## Built with
  * Front-end: [Bootstrap](https://getbootstrap.com/), [Chart.js](https://www.chartjs.org/), and [DataTables](https://datatables.net/)
    * [Money Mantra](https://money-mantra.onrender.com) uses [Webflow](https://www.webflow.com) and stills / mock ups from [Pixabay](https://pixabay.com) and [Burst](https://burst.shopify.com). Images are created with [Gimp](https://www.gimp.org/), [Figma](https://www.figma.com), and [ScreenToGif](https://www.screentogif.com/)
  * Back-end: [Flask](https://flask.palletsprojects.com)
  * Hosting: [Render](https://money-mantra.onrender.com)

## Run it locally (written for Windows and VSCode)
1) Create a directory and clone the repo in it:
```
git clone https://github.com/MissHaRin19/Budget-Tracker/tree/main
```
2) Create your virtual environment:
```
python -m venv env
```
3) Activate your virtual environment:
```
env\Scripts\activate
```
4) Install the dependencies:
```
pip install -r requirements.txt
```
5) Create the DB in Postgres (schema in repo [here](./dbCreateStatements-Postgres.txt))

6) Set your environment variables in .env file (otherwise hard code the string ```app.secret_key``` in app.py and ```engine``` in all of the ```.py``` files):
```
# App variable
SECRET_KEY=someRandomStringOfText

# DB variable
DATABASE_URL=postgres://{user}:{password}@{hostname}:{port}/{database-name}
```
7) Build and run the Flask app in VSCode

## Discussion
We started working on this in May 2026 as part of my mini project. My main goal was to replace an Excel file I was using for tracking expenses and originally this app had only 1 form and 2 or 3 pages on it. The pandemic gave me extra time to think and explore different technology so I ended up adding features that I was curious to learn about. Some of the other things I wanted to add and may work on at a later time include:
  * Tests
  * User intro / walk-through of the app
  * Improved budget tracking (i.e calculates if your weekly / monthly spending is on-track or not)
  * Dark theme
  * Suggested spend categories
