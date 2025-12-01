import streamlit as st
import pandas as pd
from datetime import date
import os

# ---------- Load CSS ----------
css_path = "theme.css"
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------- Hero Section ----------
st.image("assets/hero.jpg", use_column_width=True)
st.title("🌟 MoodFlow Planner - Emotion-Aware Scheduler")
st.image("assets/logo.jpg", width=100)

# Initialize session state for tasks
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# ---------- Mood Selection ----------
mood = st.selectbox("How are you feeling today?", ["Happy", "Sad", "Stressed", "Excited", "Neutral"])

# Display mood icon
mood_icon_path = f"assets/icons/{mood.lower()}.jpg"
if os.path.exists(mood_icon_path):
    st.image(mood_icon_path, width=50)

# ---------- Task Input Form ----------
with st.form("task_form"):
    task_name = st.text_input("Task Name")
    duration = st.number_input("Duration (hours)", 0.1, 10.0, 1.0)
    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
    submitted = st.form_submit_button("Add Task")
    
    if submitted:
        st.session_state.tasks.append({
            "task_name": task_name,
            "duration_hours": duration,
            "difficulty": difficulty
        })
        st.success(f"Task '{task_name}' added!")

# ---------- Show Current Tasks ----------
if st.session_state.tasks:
    st.subheader("Current Tasks")
    st.table(pd.DataFrame(st.session_state.tasks))

# ---------- Generate Daily Plan ----------
def generate_schedule(mood, tasks):
    schedule_text = f"Your Mood: {mood}\n\nToday's Tasks:\n"
    for i, task in enumerate(tasks):
        schedule_text += f"{i+1}. {task['task_name']} - {task['duration_hours']}h ({task['difficulty']})\n"
    return schedule_text

if st.button("Generate Daily Plan"):
    if not st.session_state.tasks:
        st.warning("Please add at least one task first!")
    else:
        schedule = generate_schedule(mood, st.session_state.tasks)
        st.subheader("📝 Your Daily Schedule")
        st.text(schedule)

        # ---------- Save to Excel ----------
        df_rows = []
        for i, task in enumerate(st.session_state.tasks):
            df_rows.append({
                "date": date.today().isoformat(),
                "mood": mood,
                "task_name": task["task_name"],
                "duration_hours": task["duration_hours"],
                "difficulty": task["difficulty"],
                "scheduled_order": i+1,
                "start_time": "",
                "end_time": "",
                "motivational_msg": f"Keep going, small steps are fine!"
            })
        df = pd.DataFrame(df_rows)
        
        if not os.path.exists("data"):
            os.makedirs("data")
        filename = "data/tasks.xlsx"
        try:
            if not os.path.exists(filename):
                df.to_excel(filename, index=False, sheet_name="Tasks")
            else:
                # Append to existing Excel
                with pd.ExcelWriter(filename, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                    startrow = writer.sheets["Tasks"].max_row if "Tasks" in writer.sheets else 0
                    df.to_excel(writer, index=False, sheet_name="Tasks", startrow=startrow, header=False)
            st.success(f"Tasks saved to {filename}")
        except PermissionError:
            st.error("Permission denied: Close tasks.xlsx if it is open in Excel and try again.")

# ---------- Mood History ----------
if os.path.exists("data/tasks.xlsx"):
    try:
        df_history = pd.read_excel("data/tasks.xlsx", sheet_name="Tasks")
        st.subheader("📊 Mood History")
        mood_counts = df_history['mood'].value_counts()
        st.bar_chart(mood_counts)
    except Exception as e:
        st.warning(f"Could not read tasks.xlsx: {e}")
