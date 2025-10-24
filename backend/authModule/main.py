from nicegui import ui
from database import SessionLocal, engine, Base
from models import User
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)  # Ensure tables created

def save_user_to_db(data: dict):
    db: Session = SessionLocal()
    try:
        # Check if user exists by email
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
            password=data["password"]  # TODO: hash password in real app
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
            db: Session = SessionLocal()
            try:
                user = db.query(User).filter(User.email == email.value).first()
                if not user:
                    ui.notify("Email not registered!", color="warning")
                    return
                if user.password != password.value:  # TODO: use hashed passwords in production
                    ui.notify("Incorrect password!", color="negative")
                    return
                ui.notify(f"Welcome back, {user.name}!", color="positive")
                # You can add navigation here after successful login
            except Exception as e:
                print("DB Error during login:", e)
                ui.notify("Error during login!", color="negative")
            finally:
                db.close()

        with ui.row().style('justify-content: space-between; margin-top: 20px'):
            ui.button('Login', on_click=login).props('color=primary round')
            ui.button('Back', on_click=lambda: ui.navigate.to('/')).props('color=secondary flat round')


ui.run()
