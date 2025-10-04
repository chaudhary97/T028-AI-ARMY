import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
import plotly.express as px
import sys
import os

# Ensure the auth.py file can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from auth import login_page

class StudentDashboard:
    def __init__(self, db_name="student_database.db"):
        self.db_name = db_name
    
    def load_risk_data(self):
        try:
            conn = sqlite3.connect(self.db_name)
            query = '''
                SELECT r.*, s.name, s.mentor_id
                FROM risk_assessment r
                JOIN students s ON r.student_id = s.student_id
                WHERE r.assessment_date = (SELECT MAX(assessment_date) FROM risk_assessment)
                ORDER BY r.overall_risk_score DESC
            '''
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Error loading risk data: {e}")
            return pd.DataFrame()

    def load_student_details(self, student_id):
        try:
            conn = sqlite3.connect(self.db_name)
            student_info = pd.read_sql_query("SELECT * FROM students WHERE student_id = ?", conn, params=[student_id])
            risk_info = pd.read_sql_query("SELECT * FROM risk_assessment WHERE student_id = ? ORDER BY assessment_date DESC LIMIT 1", conn, params=[student_id])
            attendance_data = pd.read_sql_query("SELECT date, subject, present FROM attendance WHERE student_id = ? AND date >= date('now', '-30 days')", conn, params=[student_id])
            test_data = pd.read_sql_query("SELECT test_date, subject, score FROM test_scores WHERE student_id = ? ORDER BY test_date DESC", conn, params=[student_id])
            
            # --- ADDED: Query for fee payment data ---
            fee_data = pd.read_sql_query("SELECT status, amount_due, amount_paid, due_date FROM fee_payments WHERE student_id = ?", conn, params=[student_id])

            conn.close()
            return {
                'student_info': student_info, 
                'risk_info': risk_info, 
                'attendance_data': attendance_data, 
                'test_data': test_data,
                'fee_data': fee_data # Add fee data to the output
            }
        except Exception as e:
            st.error(f"Error loading student details: {e}")
            return {}

    def create_overview_dashboard(self):
        st.title("🎓 Mentor Dashboard: Full Overview")
        st.markdown("---")
        
        risk_data = self.load_risk_data()
        if risk_data.empty:
            st.warning("No risk assessment data found.")
            return
        
        col1, col2, col3, col4 = st.columns(4)
        total_students = len(risk_data)
        at_risk = len(risk_data[risk_data['risk_level'] == 'High'])
        medium_risk = len(risk_data[risk_data['risk_level'] == 'Medium'])
        low_risk = len(risk_data[risk_data['risk_level'] == 'Low'])
        
        with col1: st.metric("Total Students", total_students)
        with col2: st.metric("High Risk", at_risk)
        with col3: st.metric("Medium Risk", medium_risk)
        with col4: st.metric("Low Risk", low_risk)
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 Risk Distribution")
            risk_counts = risk_data['risk_level'].value_counts()
            fig_pie = px.pie(values=risk_counts.values, names=risk_counts.index, title='Student Risk Distribution', color_discrete_map={'High':'red', 'Medium':'orange', 'Low':'green'})
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            st.subheader("📈 Risk Scores Distribution")
            fig_hist = px.histogram(risk_data, x='overall_risk_score', nbins=20, title='Distribution of Risk Scores')
            st.plotly_chart(fig_hist, use_container_width=True)
        st.markdown("---")
        
        # --- ADDED: Risk Factor Analysis Graphs (including Financial) ---
        st.subheader("🔍 Risk Factors Analysis")
        c1, c2, c3 = st.columns(3)
        with c1:
            fig_att = px.box(risk_data, y='attendance_risk', title='Attendance Risk', points="all")
            st.plotly_chart(fig_att, use_container_width=True)
        with c2:
            fig_acad = px.box(risk_data, y='academic_risk', title='Academic Risk', points="all")
            st.plotly_chart(fig_acad, use_container_width=True)
        with c3:
            fig_fin = px.box(risk_data, y='financial_risk', title='Financial Risk', points="all")
            st.plotly_chart(fig_fin, use_container_width=True)
        st.markdown("---")

        st.subheader("🚨 High-Risk Students")
        high_risk_df = risk_data[risk_data['risk_level'] == 'High'][['student_id', 'name', 'overall_risk_score', 'reasons', 'mentor_id']].head(10)
        st.dataframe(high_risk_df, use_container_width=True)

    def create_admin_search_view(self):
        st.title("🎓 Admin Portal: Student Search")
        st.info("Enter a student's unique ID to view their detailed report.")
        with st.form("search_form"):
            student_id_input = st.text_input("Enter Student ID (e.g., STU1001)").strip().upper()
            submitted = st.form_submit_button("🔍 Search")

        if submitted and student_id_input:
            st.markdown("---")
            self.create_student_detail_view(student_id_input)

    def create_student_detail_view(self, student_id):
        student_data = self.load_student_details(student_id)
        if not student_data or student_data['student_info'].empty:
            st.error(f"No data found for Student ID: {student_id}")
            return
        
        student_info = student_data['student_info'].iloc[0]
        st.subheader(f"📋 Student Details: {student_info['name']}")
        
        if not student_data['risk_info'].empty:
            risk_info = student_data['risk_info'].iloc[0]
            st.markdown("---")
            st.subheader("📊 Risk Assessment")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number", value=risk_info['overall_risk_score'],
                    title={'text': "Overall Risk"},
                    gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "darkred"},
                           'steps': [{'range': [0, 40], 'color': "green"}, {'range': [40, 70], 'color': "orange"}, {'range': [70, 100], 'color': 'red'}]}))
                fig_gauge.update_layout(height=200, margin=dict(l=10, r=10, t=40, b=10))
                st.plotly_chart(fig_gauge, use_container_width=True)
            with col2:
                st.metric("Risk Level", risk_info['risk_level'])
                st.info(f"**Reasons:** {risk_info['reasons']}")
            
            # --- ADDED: Individual Risk Metrics ---
            with col3:
                st.metric("Attendance Risk", f"{risk_info['attendance_risk']:.1f}%")
                st.metric("Academic Risk", f"{risk_info['academic_risk']:.1f}%")
                st.metric("Financial Risk", f"{risk_info['financial_risk']:.1f}%")
        
        # --- ADDED: Financial Status Section ---
        if not student_data['fee_data'].empty:
            st.markdown("---")
            st.subheader("💰 Financial Status")
            fee_info = student_data['fee_data'].iloc[0]
            pending_amount = fee_info['amount_due'] - fee_info['amount_paid']
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Fee Status", fee_info['status'])
            c2.metric("Amount Due", f"₹{fee_info['amount_due']:,.2f}")
            if pending_amount > 0:
                c3.metric("Pending Amount", f"₹{pending_amount:,.2f}", delta_color="inverse")
            else:
                c3.metric("Pending Amount", f"₹{pending_amount:,.2f}")

        if not student_data['attendance_data'].empty:
            st.markdown("---")
            st.subheader("📅 Recent Attendance")
            fig_att = px.line(student_data['attendance_data'].groupby('date')['present'].mean().reset_index(), x='date', y='present', markers=True)
            fig_att.update_layout(yaxis_title="Attendance %", yaxis_range=[0, 1], yaxis_tickformat=".0%")
            st.plotly_chart(fig_att, use_container_width=True)

        if not student_data['test_data'].empty:
            st.markdown("---")
            st.subheader("📝 Test Performance")
            fig_scores = px.line(student_data['test_data'], x='test_date', y='score', color='subject', markers=True)
            fig_scores.update_layout(yaxis_title="Score", yaxis_range=[0, 100])
            st.plotly_chart(fig_scores, use_container_width=True)

def run_dashboard():
    st.set_page_config(page_title="Student Dropout Prediction", page_icon="🎓", layout="wide")

    if not login_page():
        st.stop()

    # This code only runs AFTER a successful login
    dashboard = StudentDashboard()
    
    st.sidebar.title(f"Welcome, {st.session_state.username}!")
    st.sidebar.markdown(f"**Role:** {st.session_state.role.capitalize()}")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

    if st.session_state.role == 'mentor':
        st.sidebar.title("Mentor Navigation")
        page = st.sidebar.radio("Go to", ["📊 Overview Dashboard", "👤 Student Details"])
        
        if page == "📊 Overview Dashboard":
            dashboard.create_overview_dashboard()
        else:
            risk_data = dashboard.load_risk_data()
            if not risk_data.empty:
                st.sidebar.subheader("Select Student")
                student_list = risk_data['student_id'].tolist()
                student_names = risk_data.set_index('student_id')['name'].to_dict()
                selected_student = st.sidebar.selectbox("Choose a student:", student_list, format_func=lambda x: f"{x} - {student_names.get(x, 'N/A')}")
                if selected_student:
                    dashboard.create_student_detail_view(selected_student)

    elif st.session_state.role == 'admin':
        st.sidebar.title("Admin Tools")
        dashboard.create_admin_search_view()

if __name__ == "__main__":
    run_dashboard()