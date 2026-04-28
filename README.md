# Student Performance Predictor & AI Dashboard

## 📌 Project Overview
It is a comprehensive Educational Data Mining (EDM) solution designed to predict student academic outcomes and provide actionable insights. Unlike basic predictors, this system uses a **Hybrid AI Approach**—combining structured academic data (attendance, scores) with unstructured text data (teacher remarks) using NLP.

The goal is to provide teachers with an "Early Warning System" to identify at-risk students and offer students a personalized roadmap for improvement.

## 🚀 Key Features
* **Hybrid AI Engine:** Integrates numerical features with text-based feedback using **NLP (NLTK & TF-IDF)**.
* **Multi-Model Comparison:** Evaluates Logistic Regression, Random Forest, Decision Trees, and SVM to select the most accurate predictor.
* **Dual-Role Portal:** * **Teacher Dashboard:** Class-wide performance analytics, disciplinary trends, and automated "At-Risk" student alerts.
    * **Student Dashboard:** Personal GPA tracking vs. class average, and real-time AI-generated grade predictions.
* **Interactive Visualizations:** Powered by **Plotly**, featuring Gauge charts for performance standing and grouped histograms for course-wise analysis.
* **Recommendation System:** An automated engine that provides personalized academic strategies (e.g., attendance warnings or tutoring suggestions) based on model output.

## 🛠️ Technology Stack
* **Machine Learning:** Scikit-learn (Random Forest, SVM, Logistic Regression)
* **NLP:** NLTK, TF-IDF Vectorization, Lemmatization
* **Backend:** Flask (Python)
* **Frontend:** HTML5, Plotly.js (for Glass Fusion UI Dashboard)
* **Database:** SQLite3
* **Data Science:** Pandas, NumPy, Seaborn, Matplotlib

## 📊 Model Performance
The system evaluates multiple algorithms. Current training results:
- **Random Forest:** Highest Accuracy for complex patterns.
- **SVM:** Robust performance on normalized feature sets.

🔧 Installation
Clone: git clone https://github.com/Ali-Akbar31/Student-Performance-Predictor-Dashboard.git

Install: pip install flask pandas scikit-learn nltk plotly joblib

Run: python app.py

Developed by Ali Akbar | Freelance Data Scientist
