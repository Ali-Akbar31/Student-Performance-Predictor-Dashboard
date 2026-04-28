# app.py (Final Nex Edu Fusion Refined Version)
from flask import Flask, render_template, request, redirect, session
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import joblib  
import os
import re
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)
app.secret_key = 'student_tracker_secure_key'

# ==========================================
# 1. LOAD AND PREPARE DATASET
# ==========================================
df = pd.read_csv('clean_dataset.csv')
df.columns = df.columns.str.strip()

df_ml = df.copy()
categorical_columns = ['Gender', 'Course', 'Section', 'Study_Habits', 'Disciplinary_Record', 'Internship_Status', 'Project_Title']

for col in categorical_columns:
    if col in df_ml.columns:
        le = LabelEncoder()
        df_ml[col] = le.fit_transform(df_ml[col].astype(str))

# ==========================================
# 2. SETUP SQLITE DATABASE & USERS
# ==========================================
def setup_database():
    conn = sqlite3.connect('student_db.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS portal_users')
    cursor.execute('''CREATE TABLE portal_users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        username TEXT UNIQUE, 
                        password TEXT, 
                        role TEXT, 
                        student_id TEXT)''')
    
    cursor.execute("INSERT INTO portal_users (username, password, role, student_id) VALUES (?, ?, ?, ?)", 
                   ('faculty', '12345', 'teacher', None))
    conn.commit()
    conn.close()

setup_database()

# ==========================================
# 3. LOAD MACHINE LEARNING MODELS
# ==========================================
try:
    best_model = joblib.load('best_student_model.pkl') 
    scaler = joblib.load('scaler_obj.pkl')
    vectorizer = joblib.load('tfidf_obj.pkl') 
    target_encoder = joblib.load('target_encoder.pkl') 
    ml_ready = True
    print("\n✅ Nex Edu ML Engine Loaded Successfully!")
except Exception as error:
    print(f"\n❌ ML Engine Failed to Load: {error}")
    ml_ready = False

# Nex Edu Chart Styling Helper
def get_chart_layout(title=""):
    return {
        'title': title,
        'paper_bgcolor': 'rgba(0,0,0,0)', # Full Glass Fusion transparency
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {'family': 'Poppins, sans-serif', 'color': '#475569'},
        'margin': {'t': 60, 'b': 20, 'l': 10, 'r': 10},
        'hovermode': 'closest', # Better interaction
        'xaxis': {'showgrid': True, 'gridcolor': 'rgba(0,0,0,0.05)', 'zeroline': False},
        'yaxis': {'showgrid': True, 'gridcolor': 'rgba(0,0,0,0.05)', 'zeroline': False},
    }

# ==========================================
# 4. WEB ROUTES
# ==========================================

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username', '').strip()
        pwd = request.form.get('password', '').strip()
        
        # Faculty Login
        conn = sqlite3.connect('student_db.db')
        conn.row_factory = sqlite3.Row
        account = conn.execute('SELECT * FROM portal_users WHERE username = ? AND password = ?', (user, pwd)).fetchone()
        conn.close()
        
        if account and account['role'] == 'teacher':
            session['username'] = account['username']
            session['role'] = account['role']
            session['student_id'] = None
            return redirect('/faculty')
            
        # Student Login (Dynamic CSV Check)
        student_match = df[df['Student_ID'].astype(str).str.strip().str.upper() == user.upper()]
        
        if not student_match.empty and pwd == '123':
            actual_id = student_match.iloc[0]['Student_ID']
            session['username'] = str(actual_id)
            session['role'] = 'student'
            session['student_id'] = str(actual_id)
            return redirect('/scholar')
        
        return render_template('login.html', error="Invalid Credentials. Please enter a valid Teacher account or a valid Student ID with password '123'.")
            
    return render_template('login.html')

@app.route('/faculty')
def faculty_dashboard():
    if session.get('role') != 'teacher':
        return redirect('/')
   
    # 1. Bar Chart (Grades)
    if 'Course' in df.columns:
        chart_df = df.fillna({'Course': 'Unknown'})
        fig1 = px.histogram(chart_df, x='Course', color='Student_Grade_Band',
                            barmode='group',
                            labels={'Student_Grade_Band': 'Performance Level'},
                            color_discrete_sequence=px.colors.qualitative.Pastel)
    else:
        fig1 = px.pie(df, names='Student_Grade_Band')
   
    fig1.update_layout(get_chart_layout('Performance Level Distribution by Course'))
    fig1.update_traces(hovertemplate="Course: %{x}<br>Count: %{y}<extra></extra>") # Refined hover

    # 2. Pie Chart (Discipline)
    if 'Disciplinary_Record' in df.columns:
        d_series = df['Disciplinary_Record'].astype(str).str.strip()
        d_series = d_series[~d_series.isin(['nan', 'None', 'NaN', ''])]

        counts_map = d_series.value_counts()
        labels = counts_map.index.tolist()  
        values = counts_map.values.tolist() 

        color_map = {
            'Excellent': '#10b981', 'Good': '#3b82f6',
            'Needs Improvement': '#f59e0b', 'Probation': '#f97316', 'Warning': '#ef4444'
        }
        colors = [color_map.get(l, '#94a3b8') for l in labels]

        fig2 = go.Figure(data=[go.Pie(
            labels=labels, values=values, hole=0.6,
            marker=dict(colors=colors, line=dict(color='#ffffff', width=2)),
            textinfo='percent+label', hoverinfo='label+value'
        )])

        fig2.update_layout(get_chart_layout('Class Conduct Record'))
        fig2.update_layout(showlegend=False,
            annotations=[dict(text='Class<br>Conduct', x=0.5, y=0.5, font_size=18, showarrow=False, font_family='Poppins', font_color='#1e293b')]
        )
    else:
        fig2 = go.Figure()

    # 3. Alerts Table & KPIs
    all_alerts = df[df['Student_Grade_Band'].isin(['Poor', 'Fail'])]
    alert_table_df = all_alerts
    # Teacher dash table with clean indigo styling
    table_html = alert_table_df.to_html(classes='table table-glass text-center align-middle', index=False)
   
    kpis = {'total': len(df), 'alerts': len(all_alerts)}
   
    return render_template('teacher_dashboard.html', graph1=fig1.to_json(), graph2=fig2.to_json(), table=table_html, kpis=kpis)

@app.route('/scholar')
def scholar_dashboard():
    if session.get('role') != 'student': 
        return redirect('/')
    
    student_id = session.get('student_id')
    student_data = df[df['Student_ID'] == student_id]
    
    if student_data.empty: 
        return "Student Not Found in Database."
    
    # 1. Live ML Prediction
    predicted_grade = "N/A"
    if ml_ready:
        try:
            cols_to_remove = ['Student_ID', 'Registration_No', 'Student_Grade_Band', 'Target_Grade', 
                              'Final_Obtained_Score', 'Teacher_Remarks', 'Extracurricular_Feedback', 
                              'Combined_Text', 'Cleaned_Text']
            
            num_data = df_ml.drop(columns=[c for c in cols_to_remove if c in df_ml.columns]).select_dtypes(include=[np.number])
            scaled_numbers = scaler.transform(num_data.loc[student_data.index])
            
            t_remark = str(student_data['Teacher_Remarks'].fillna("").iloc[0]) if 'Teacher_Remarks' in student_data.columns else ""
            e_feedback = str(student_data['Extracurricular_Feedback'].fillna("").iloc[0]) if 'Extracurricular_Feedback' in student_data.columns else ""
            combined_text = (t_remark + " " + e_feedback).lower()
            
            clean_text = re.sub(r'[^\w\s]', '', combined_text) 
            text_features = vectorizer.transform([clean_text]).toarray()
            
            combined_input = np.hstack((scaled_numbers, text_features))
            prediction = best_model.predict(combined_input)[0]
            predicted_grade = target_encoder.inverse_transform([prediction])[0]
        except Exception as e:
            print(f"Prediction Error: {e}")
            predicted_grade = student_data['Student_Grade_Band'].iloc[0] if 'Student_Grade_Band' in student_data.columns else "N/A"
    else:
        predicted_grade = student_data['Student_Grade_Band'].iloc[0] if 'Student_Grade_Band' in student_data.columns else "N/A"

    # Define dynamic color base for Student Dashboard
    grade_colors = {'Poor': '#ef4444', 'Fail': '#ef4444', 'Average': '#f59e0b', 'Good': '#10b981', 'Excellent': '#10b981'}
    theme_color = grade_colors.get(predicted_grade, '#4f46e5')

    # 2. Gauge Chart (Score)
    if 'Final_Obtained_Score' in df.columns:
        student_score = float(student_data['Final_Obtained_Score'].iloc[0])
        gauge_chart = go.Figure(go.Indicator(
            mode = "gauge+number", value = student_score, title = {'text': "Final Obtained Score"},
            number = {'font': {'color': theme_color}}, # dynamic number color
            gauge = {
                'axis': {'range': [None, 100], 'tickfont': {'color': '#475569'}}, 
                'bar': {'color': theme_color}, # dynamic bar color
                'bgcolor': 'rgba(0,0,0,0.05)',
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.1)'}, # Poor background steps
                    {'range': [50, 80], 'color': 'rgba(245, 158, 11, 0.1)'}, # Avg background steps
                    {'range': [80, 100], 'color': 'rgba(16, 185, 129, 0.1)'}, # Good background steps
                ]
            }
        ))
        
        # apply transparent layout safely
        temp_layout = get_chart_layout('Final Exam Standing')
        temp_layout['xaxis'] = None # Remove grid for gauge
        temp_layout['yaxis'] = None
        gauge_chart.update_layout(temp_layout)
        
        json_gauge = gauge_chart.to_json()
    else:
        json_gauge = None

    # 3. Bar Chart (Marks Breakdown)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    ignore_words = ['id', 'registration', 'percentage', 'attended', 'total', 'age', 'semester', 'gpa', 'cgpa']
    graph_columns = [col for col in numeric_cols if not any(word in col.lower() for word in ignore_words)][-8:] 
    
    if graph_columns:
        my_marks = student_data[graph_columns].iloc[0].fillna(0).round(1).tolist()
        class_average = df[graph_columns].mean().fillna(0).round(1).tolist()
        
        bar_chart = go.Figure()
        bar_chart.add_trace(go.Bar(x=graph_columns, y=my_marks, name='My Marks', marker_color=theme_color))
        bar_chart.add_trace(go.Bar(x=graph_columns, y=class_average, name='Class Avg', marker_color='#cbd5e1'))
        
        # apply layout and adjust
        bar_layout = get_chart_layout('Performance Analytics vs Class')
        bar_layout['barmode'] = 'group'
        bar_layout['xaxis']['tickangle'] = -45
        bar_chart.update_layout(bar_layout)
        
        json_bar = bar_chart.to_json()
    else:
        json_bar = None

    # =========================================================
    # 4. ACTIONABLE STRATEGIES GENERATOR (Assignment 4 Task)
    # =========================================================
    recommendations = []
    
    # Check Attendance (Tries to find 'Attendance_Percentage' or similar column)
    att_col = next((c for c in df.columns if 'attend' in c.lower()), None)
    if att_col:
        att = float(student_data[att_col].iloc[0])
        if att < 75:
            recommendations.append("⚠️ Your attendance is low. Try to attend more classes to cover missing concepts.")
            
    # Check Assignment Performance
    if 'Avg_Assignment_Score' in df.columns:
        assign_score = float(student_data['Avg_Assignment_Score'].iloc[0])
        if assign_score < 60:
            recommendations.append("📚 Your assignment performance is weak. Consider taking extra practice or tutoring.")

    # Check AI Risk Level
    if predicted_grade in ['Poor', 'Fail']:
        recommendations.append("🚨 You are at risk of underperforming. Please schedule a meeting with your counselor.")
        
    # If everything is good
    if not recommendations:
        recommendations.append("🌟 You are doing great! Maintain your current study habits and consistency.")

    return render_template('student_dashboard.html', s=student_data.iloc[0], live_grade=predicted_grade, graph_gauge=json_gauge, graph_bar=json_bar, strategies=recommendations)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    print("\n🚀 Nex Edu Fusion Server Running at: http://127.0.0.1:5000\n")
    app.run(debug=True, port=5000)