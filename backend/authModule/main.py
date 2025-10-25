from nicegui import ui, app
from database import SessionLocal, engine, Base
from models import User, HealthRecord
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from datetime import datetime, timezone
from pdf_utils import generate_user_pdf
import os

current_user_email = None

Base.metadata.create_all(bind=engine)

def save_user_to_db(data: dict):
    db: Session = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == data['email']).first()
        if existing:
            ui.notify("Email already registered!", color="warning")
            return False
        user = User(
            email=data["email"],
            name=data["name"],
            phone=data.get("phone"),
            age=int(data.get("age")) if data.get("age") else None,
            gender=data.get("gender"),
            password=data["password"]
        )
        db.add(user)
        db.commit()
        return True
    except Exception as e:
        print("DB Error:", e)
        ui.notify("Error saving data!", color="negative")
        return False
    finally:
        db.close()

def human_readable_time_diff(last_time):
    """Convert datetime difference to human-friendly text."""
    if not last_time:
        return "No updates yet"
    
    # Parse ISO string to datetime if needed
    if isinstance(last_time, str):
        try:
            last_time = datetime.fromisoformat(last_time.replace('Z', '+00:00'))
        except:
            return "No updates yet"
    
    now = datetime.now(timezone.utc)
    
    # Make timezone-aware if needed
    if last_time.tzinfo is None:
        last_time = last_time.replace(tzinfo=timezone.utc)
    
    diff = now - last_time
    seconds = diff.total_seconds()

    if seconds < 60:
        return f"Updated {int(seconds)} seconds ago"
    elif seconds < 3600:
        return f"Updated {int(seconds // 60)} minutes ago"
    elif seconds < 86400:
        return f"Updated {int(seconds // 3600)} hours ago"
    elif seconds < 31536000:
        return f"Updated {int(seconds // 86400)} days ago"
    else:
        return f"Updated {int(seconds // 31536000)} years ago"

def logout():
    global current_user_email
    current_user_email = None
    ui.notify('Logged out successfully.', color='info')
    ui.navigate.to('/')

@app.get("/download_pdf")
def download_pdf():
    pdf_path = "carebot_report.pdf"
    if not os.path.exists(pdf_path):
        return {"error": "PDF not found. Please submit a health record first."}
    return FileResponse(
        path=pdf_path, 
        filename="carebot_report.pdf", 
        media_type="application/pdf"
    )

@ui.page('/')
def landing_page():
    with ui.column().style('max-width: 400px; margin: auto; margin-top: 100px; text-align: center;'):
        ui.label('Welcome to Care Bot!').style('font-size: 26px; font-weight: 600; color: #2c3e50; margin-bottom: 20px')
        ui.button('Register', on_click=lambda: ui.navigate.to('/register')).props('color=primary round')
        ui.button('Login', on_click=lambda: ui.navigate.to('/login')).props('color=secondary flat round')

@ui.page('/register')
def register_page():
    with ui.column().style('max-width: 400px; margin: auto; margin-top: 50px;'):
        ui.label('Register New User').style('font-weight: 600; font-size: 22px; color: #2c3e50; margin-bottom: 15px')
        email = ui.input('Email').props('type=email outlined dense')
        name = ui.input('Full Name').props('outlined dense')
        phone = ui.input('Phone Number').props('outlined dense')
        age = ui.input('Age').props('type=number outlined dense')
        gender = ui.select(['Male', 'Female', 'Other'], label='Gender').props('outlined dense')
        password = ui.input('Password').props('type=password outlined dense')

        def submit():
            data = {
                'email': email.value,
                'name': name.value,
                'phone': phone.value,
                'age': age.value,
                'gender': gender.value,
                'password': password.value
            }
            if save_user_to_db(data):
                ui.notify('Registration successful!', color='positive')

        with ui.row().style('justify-content: space-between; margin-top: 20px'):
            ui.button('Register', on_click=submit).props('color=primary round')
            ui.button('Back', on_click=lambda: ui.navigate.to('/')).props('color=secondary flat round')

@ui.page('/login')
def login_page():
    with ui.column().style('max-width: 400px; margin: auto; margin-top: 50px;'):
        ui.label('User Login').style('font-weight: 600; font-size: 22px; color: #2c3e50; margin-bottom: 15px')
        
        email = ui.input('Email').props('type=email outlined dense')
        password = ui.input('Password').props('type=password outlined dense')

        def login():
            global current_user_email
            db: Session = SessionLocal()
            try:
                user = db.query(User).filter(User.email == email.value).first()
                if not user:
                    ui.notify("Email not registered!", color="warning")
                    return
                if user.password != password.value:
                    ui.notify("Incorrect password!", color="negative")
                    return
                
                current_user_email = user.email
                
                # IMPORTANT: Generate PDF on login if records exist
                has_records = db.query(HealthRecord).filter(HealthRecord.user_id == user.id).first()
                if has_records:
                    print(f"Generating PDF for user {user.id}")  # Debug print
                    success = generate_user_pdf(user.id)
                    if success:
                        print("PDF generated successfully on login")
                    else:
                        print("PDF generation failed")
                
                ui.notify(f"Welcome back, {user.name}!", color="positive")
                ui.navigate.to('/health-record')
            except Exception as e:
                print("DB Error during login:", e)
                ui.notify("Error during login!", color="negative")
            finally:
                db.close()

        with ui.row().style('justify-content: space-between; margin-top: 20px'):
            ui.button('Login', on_click=login).props('color=primary round')
            ui.button('Back', on_click=lambda: ui.navigate.to('/')).props('color=secondary flat round')

@ui.page('/health-record')
def health_record_page():
    global current_user_email
    if not current_user_email:
        ui.label("Access denied. Please log in first.")
        ui.button("Go to Login", on_click=lambda: ui.navigate.to('/login'))
        return

    db: Session = SessionLocal()
    user = db.query(User).filter(User.email == current_user_email).first()
    has_records = db.query(HealthRecord).filter(HealthRecord.user_id == user.id).first() is not None
    db.close()

    with ui.column().style('max-width: 500px; margin: auto; margin-top: 50px'):
        ui.label(f"Welcome {user.name}! Submit your health summary").style(
            'font-weight: 600; font-size: 20px; color: #2c3e50'
        )
        
        problem_input = ui.input('Problem Name').props('outlined dense')
        summary_input = ui.textarea('Summary').props('outlined dense autogrow')
        reported_date_input = ui.input('Reported On').props('type=date outlined dense')

        def submit():
            db = SessionLocal()
            try:
                record = HealthRecord(
                    user_id=user.id,
                    problem=problem_input.value,
                    summary=summary_input.value,
                    reported_on=reported_date_input.value,
                    created_on=datetime.utcnow()
                )
                db.add(record)
                
                # CHANGE: Update user's last_updated in database
                user_obj = db.query(User).filter(User.id == user.id).first()
                user_obj.last_updated = datetime.now(timezone.utc).isoformat()
                
                db.commit()
                
                success = generate_user_pdf(user.id)
                if success:
                    ui.notify('Record saved and PDF generated!', color='positive')
                    ui.navigate.to('/health-record')  # Refresh page
                else:
                    ui.notify('Record saved but PDF generation failed!', color='warning')
                    
            except Exception as e:
                print("Error saving record:", e)
                ui.notify('Error saving record!', color='negative')
            finally:
                db.close()

        with ui.row().style('justify-content: space-between; margin-top: 20px'):
            ui.button('Submit', on_click=submit).props('color=primary round')
            ui.button('Logout', on_click=lambda: logout()).props('color=secondary flat round')

        # CHANGE: Show download button only if user has records
        if has_records:
            ui.button('Download PDF Report', on_click=lambda: ui.open('/download_pdf', new_tab=True)).props(
                'color=positive round'
            ).style('margin-top: 20px')

            # CHANGE: Time label reads from database
            time_label = ui.label(human_readable_time_diff(user.last_updated)).style(
                'color: gray; font-size: 14px; margin-top: 10px'
            )
            
            ui.timer(5.0, lambda: time_label.set_text(human_readable_time_diff(user.last_updated)))

ui.run()
