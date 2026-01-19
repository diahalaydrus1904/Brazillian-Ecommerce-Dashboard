# Brazilian E-Commerce Data Analysis & Dashboard

## Project Overview

This project is a **data analysis and visualization dashboard** built using a Brazilian E-Commerce public dataset. The objective is to analyze customer transactions and business performance through a structured data analysis workflow and present the insights in a clear and accessible format using **Streamlit**.

The project covers the full analytics pipeline, starting from **exploratory data analysis (EDA)** and **data preprocessing**, followed by **business insight generation**, and finalized with an **interactive dashboard**.

---

## Objectives

* Perform end-to-end data analysis using a real-world e-commerce dataset
* Answer business-relevant analytical questions using data
* Create effective and readable data visualizations
* Deploy a dashboard using Streamlit for insight exploration

---

## Business Questions

The analysis focuses on answering questions such as:

* How much total revenue is generated each month?
* Which product categories generate the highest revenue?
* Which province has the highest number of customers?
* Is there a relationship between delivery time and customer review scores?
* What is the average delivery time, and which regions experience delays most frequently?
* Which sellers generate the highest revenue?
* Which product categories have the highest and lowest average review scores?

---

## Analysis Process

1. **Data Understanding**
   Exploring dataset structure, tables, and relationships

2. **Data Cleaning & Preprocessing**
   Handling missing values, formatting date columns, and merging datasets

3. **Exploratory Data Analysis (EDA)**
   Identifying trends and patterns using descriptive statistics and visualizations

4. **Insight Generation**
   Interpreting analytical results to answer business questions

5. **Visualization**
   Designing clear charts to communicate insights effectively

---

## Dashboard

The final output of this project is an **interactive Streamlit dashboard** that presents key insights from the analysis.

### Dashboard Features

* Date-based filtering to explore metrics across different time ranges
* Visualizations summarizing transaction trends and business performance
* Clean and minimal layout focused on readability

---

## Project Structure

```text
.
├── data/                 # Raw and processed datasets
├── dashboard.py          # Streamlit dashboard script
├── requirements.txt      # Project dependencies
├── README.md             # Project documentation
```

---

## Setup Virtual Environment

It is recommended to use a virtual environment to manage project dependencies.

### Create virtual environment

```bash
python -m venv venv
```

### Activate virtual environment

**Windows**

```bash
venv\Scripts\activate
```

**macOS / Linux**

```bash
source venv/bin/activate
```

---

## Install Required Libraries

All required libraries are listed in `requirements.txt`.
It is recommended to install dependencies using this file instead of installing libraries manually.

```bash
pip install -r requirements.txt
```

---

## Run the Dashboard

Make sure you are in the project root directory and the virtual environment is activated.

```bash
streamlit run dashboard.py
```

If your dashboard file is located in a different folder, adjust the path accordingly, for example:

```bash
streamlit run src/dashboard.py
```

---

## Technologies Used

* **Python**
* **Pandas & NumPy** – Data manipulation and analysis
* **Matplotlib / Seaborn** – Data visualization
* **Streamlit** – Dashboard deployment

---

## Key Takeaways

* Demonstrates a complete data analysis workflow from raw data to insights
* Applies business-oriented thinking in defining analytical questions
* Presents insights through effective visual storytelling
* Showcases practical experience in building and deploying dashboards with Streamlit
