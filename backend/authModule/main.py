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
    
    if isinstance(last_time, str):
        try:
            last_time = datetime.fromisoformat(last_time.replace('Z', '+00:00'))
        except:
            return "No updates yet"
    
    now = datetime.now(timezone.utc)
    
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
    # Add custom CSS for animations
    ui.add_head_html('''
        <style>
            @keyframes float {
                0%, 100% { transform: translateY(0px); }
                50% { transform: translateY(-20px); }
            }
            .float-animation {
                animation: float 3s ease-in-out infinite;
            }
        </style>
    ''')
    
    # Top Navbar
    with ui.header().classes('fixed top-0 left-0 right-0').style(
        'height: 70px; background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); '
        'box-shadow: 0 2px 10px rgba(0,0,0,0.1); z-index: 1000;'
    ):
        with ui.row().classes('w-full items-center justify-between').style('padding: 0 50px; max-width: 100%;'):
            with ui.row().classes('items-center gap-3'):
                ui.label('🏥').style('font-size: 32px;')
                ui.label('Care Bot').style(
                    'font-size: 24px; font-weight: 700; '
                    'background: linear-gradient(45deg, #667eea, #764ba2); '
                    '-webkit-background-clip: text; -webkit-text-fill-color: transparent;'
                )
            
            with ui.row().classes('gap-3'):
                ui.button('Articles', on_click=lambda: ui.navigate.to('/articles')).props('flat').style(
                    'padding: 10px 24px; border-radius: 10px; font-weight: 600; font-size: 15px; '
                    'color: #1e293b; border: 2px solid #e2e8f0;'
                )
                ui.button('About', on_click=lambda: ui.navigate.to('/about')).props('flat').style(
                    'padding: 10px 24px; border-radius: 10px; font-weight: 600; font-size: 15px; '
                    'color: #1e293b; border: 2px solid #e2e8f0;'
                )
                ui.button('Contact', on_click=lambda: ui.navigate.to('/contact')).props('flat').style(
                    'padding: 10px 24px; border-radius: 10px; font-weight: 600; font-size: 15px; '
                    'color: #1e293b; border: 2px solid #e2e8f0;'
                )
                ui.button('Login', on_click=lambda: ui.navigate.to('/login')).props('flat').style(
                    'padding: 10px 24px; border-radius: 10px; font-weight: 600; font-size: 15px; '
                    'color: #1e293b; border: 2px solid #e2e8f0;'
                )
                ui.button('Register', on_click=lambda: ui.navigate.to('/register')).props('unelevated').style(
                    'padding: 10px 24px; border-radius: 10px; font-weight: 600; font-size: 15px; '
                    'background: linear-gradient(135deg, #667eea, #764ba2); color: white; '
                    'box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);'
                )
    
    # Hero Section
    with ui.column().classes('w-full items-center justify-center').style(
        'min-height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
        'padding: 140px 20px 60px; text-align: center;'
    ):
        with ui.column().classes('items-center').style('max-width: 800px;'):
            ui.label('🏥').classes('float-animation').style('font-size: 80px; margin-bottom: 24px;')
            
            ui.label('Your Personal Healthcare Management System').style(
                'font-size: 56px; font-weight: 800; color: white; margin-bottom: 20px; '
                'line-height: 1.2; letter-spacing: -1px;'
            )
            
            ui.label(
                'Track your medical history, organize health records, and generate '
                'comprehensive reports. Your wellness journey starts here.'
            ).style(
                'font-size: 22px; color: rgba(255, 255, 255, 0.9); margin-bottom: 40px; '
                'line-height: 1.6; max-width: 650px;'
            )
            
            with ui.row().classes('gap-5 justify-center').style('margin-bottom: 50px;'):
                ui.button('Get Started →', on_click=lambda: ui.navigate.to('/register')).props('unelevated').style(
                    'padding: 18px 40px; border-radius: 14px; font-weight: 700; font-size: 17px; '
                    'background: white; color: #667eea; box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15); '
                    'text-transform: none;'
                )
                ui.button('Sign In', on_click=lambda: ui.navigate.to('/login')).props('unelevated').style(
                    'padding: 18px 40px; border-radius: 14px; font-weight: 700; font-size: 17px; '
                    'background: rgba(255, 255, 255, 0.2); color: white; '
                    'border: 2px solid rgba(255, 255, 255, 0.3); backdrop-filter: blur(10px); '
                    'text-transform: none;'
                )
            
            with ui.row().classes('items-center gap-3').style(
                'padding: 15px 30px; background: rgba(255, 255, 255, 0.15); '
                'border: 2px solid rgba(255, 255, 255, 0.3); border-radius: 50px; '
                'color: white; font-size: 15px; font-weight: 600; backdrop-filter: blur(10px);'
            ):
                ui.label('✨').style('font-size: 24px;')
                ui.label('Wellness Made Simple.')
    
    # Features Section
    with ui.column().classes('w-full').style('background: white; padding: 80px 50px;'):
        with ui.column().classes('items-center').style('max-width: 1200px; margin: 0 auto;'):
            ui.label('Why Choose Care Bot?').style(
                'text-align: center; font-size: 40px; font-weight: 700; '
                'color: #1e293b; margin-bottom: 50px;'
            )
            
            with ui.grid(columns=3).classes('gap-8 w-full'):
                features = [
                    ('📝', 'Smart Organization', 'Keep all your health records organized in one place with intelligent categorization and tagging.'),
                    ('📄', 'Instant PDF Reports', 'Generate professional health reports in PDF format instantly, ready to share with your doctor.'),
                    ('📊', 'Track Your Progress', 'Visualize your health journey with detailed history and insights that help you stay informed.'),
                    ('⚡', 'Lightning Fast', 'Access your health records instantly from anywhere with our optimized cloud infrastructure.'),
                    ('🌐', 'Multi-Device Access', 'Use Care Bot seamlessly across desktop, tablet, and mobile - your data syncs automatically.'),
                    ('🎯', 'Simple & Intuitive', 'Clean, user-friendly interface designed for everyone - no technical knowledge required.')
                ]
                
                for icon, title, desc in features:
                    with ui.card().style(
                        'background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05)); '
                        'border: 2px solid rgba(102, 126, 234, 0.1); border-radius: 16px; '
                        'padding: 35px; text-align: center; transition: all 0.3s ease;'
                    ):
                        ui.label(icon).style('font-size: 48px; margin-bottom: 20px;')
                        ui.label(title).style(
                            'font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 12px;'
                        )
                        ui.label(desc).style('font-size: 15px; color: #64748b; line-height: 1.6;')




@ui.page('/articles')
def articles_page():
    # Top Navbar - CONSISTENT ORDER
    with ui.header().classes('fixed top-0 left-0 right-0').style(
        'height: 70px; background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); '
        'box-shadow: 0 2px 10px rgba(0,0,0,0.1); z-index: 1000;'
    ):
        with ui.row().classes('w-full items-center justify-between').style('padding: 0 50px; max-width: 100%;'):
            with ui.row().classes('items-center gap-3'):
                ui.label('🏥').style('font-size: 32px;')
                ui.label('Care Bot').style(
                    'font-size: 24px; font-weight: 700; '
                    'background: linear-gradient(45deg, #667eea, #764ba2); '
                    '-webkit-background-clip: text; -webkit-text-fill-color: transparent;'
                )
            
            with ui.row().classes('gap-3'):
                ui.button('Home', on_click=lambda: ui.navigate.to('/')).props('flat').style(
                    'padding: 10px 24px; border-radius: 10px; font-weight: 600; font-size: 15px; '
                    'color: #1e293b; border: 2px solid #e2e8f0;'
                )
                ui.button('About', on_click=lambda: ui.navigate.to('/about')).props('flat').style(
                    'padding: 10px 24px; border-radius: 10px; font-weight: 600; font-size: 15px; '
                    'color: #1e293b; border: 2px solid #e2e8f0;'
                )
                ui.button('Contact', on_click=lambda: ui.navigate.to('/contact')).props('flat').style(
                    'padding: 10px 24px; border-radius: 10px; font-weight: 600; font-size: 15px; '
                    'color: #1e293b; border: 2px solid #e2e8f0;'
                )
                ui.button('Login', on_click=lambda: ui.navigate.to('/login')).props('flat').style(
                    'padding: 10px 24px; border-radius: 10px; font-weight: 600; font-size: 15px; '
                    'color: #1e293b; border: 2px solid #e2e8f0;'
                )
                ui.button('Register', on_click=lambda: ui.navigate.to('/register')).props('unelevated').style(
                    'padding: 10px 24px; border-radius: 10px; font-weight: 600; font-size: 15px; '
                    'background: linear-gradient(135deg, #667eea, #764ba2); color: white; '
                    'box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);'
                )
    
    # Main Content
    with ui.column().classes('w-full').style('background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%); padding: 100px 20px 60px; min-height: 100vh;'):
        with ui.column().classes('items-center').style('max-width: 1400px; margin: 0 auto;'):
            
            # Hero Section
            with ui.column().classes('items-center text-center').style('margin-bottom: 60px;'):
                ui.label('Health & Wellness Articles').style(
                    'font-size: 48px; font-weight: 800; color: #1e293b; margin-bottom: 20px; '
                    'background: linear-gradient(45deg, #667eea, #764ba2); '
                    '-webkit-background-clip: text; -webkit-text-fill-color: transparent;'
                )
                ui.label('Expert insights and tips for a healthier lifestyle').style(
                    'font-size: 20px; color: #64748b; max-width: 700px; line-height: 1.6;'
                )
            
            # Featured Article
            with ui.card().style(
                'width: 100%; padding: 50px; border-radius: 20px; margin-bottom: 50px; '
                'background: linear-gradient(135deg, #667eea, #764ba2); '
                'box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);'
            ):
                with ui.row().classes('items-center gap-3').style('margin-bottom: 15px;'):
                    ui.label('⭐').style('font-size: 28px;')
                    ui.label('FEATURED ARTICLE').style('font-size: 14px; font-weight: 700; color: white; letter-spacing: 2px;')
                
                ui.label('10 Essential Habits for a Healthier Heart').style(
                    'font-size: 36px; font-weight: 800; color: white; margin-bottom: 15px; line-height: 1.3;'
                )
                
                ui.label(
                    'Cardiovascular health is the foundation of overall wellness. Learn the scientifically-proven '
                    'daily habits that can significantly reduce your risk of heart disease, lower blood pressure, '
                    'and improve your quality of life.'
                ).style('font-size: 18px; color: rgba(255, 255, 255, 0.95); margin-bottom: 25px; line-height: 1.7;')
                
                with ui.column().classes('gap-3').style('margin-bottom: 25px;'):
                    habits = [
                        '💪 Exercise for 30 minutes daily - Even moderate activity strengthens your heart',
                        '🥗 Adopt a Mediterranean diet - Rich in omega-3s and antioxidants',
                        '😴 Prioritize 7-9 hours of quality sleep - Essential for heart recovery',
                        '🧘 Manage stress through meditation - Reduces cortisol and inflammation',
                        '🚭 Avoid tobacco and limit alcohol - Critical for vascular health'
                    ]
                    for habit in habits:
                        ui.label(habit).style('font-size: 16px; color: white; line-height: 1.8;')
                
                ui.label('5 min read • Updated Oct 2025').style('font-size: 14px; color: rgba(255, 255, 255, 0.8);')
            
            # Articles Grid
            with ui.grid(columns=3).classes('gap-6 w-full'):
                
                articles = [
                    {
                        'icon': '🧠',
                        'category': 'Mental Health',
                        'title': 'Understanding Anxiety and Stress Management',
                        'excerpt': 'Discover evidence-based techniques to manage anxiety, reduce stress, and improve mental clarity. Learn about cognitive behavioral strategies, breathing exercises, and mindfulness practices.',
                        'read_time': '7 min read',
                        'color': 'rgba(59, 130, 246, 0.1)'
                    },
                    {
                        'icon': '🍎',
                        'category': 'Nutrition',
                        'title': 'The Science of Balanced Nutrition',
                        'excerpt': 'A comprehensive guide to macronutrients, micronutrients, and building sustainable eating habits. Understand portion control, meal timing, and nutrient-dense food choices.',
                        'read_time': '10 min read',
                        'color': 'rgba(34, 197, 94, 0.1)'
                    },
                    {
                        'icon': '💤',
                        'category': 'Sleep Health',
                        'title': 'Improving Your Sleep Quality',
                        'excerpt': 'Master the art of restorative sleep with proven sleep hygiene practices. Learn about circadian rhythms, sleep cycles, and creating the optimal bedroom environment.',
                        'read_time': '6 min read',
                        'color': 'rgba(147, 51, 234, 0.1)'
                    },
                    {
                        'icon': '🏃',
                        'category': 'Fitness',
                        'title': 'Exercise Guidelines for All Ages',
                        'excerpt': 'Age-appropriate fitness routines from childhood to senior years. Includes strength training, cardio, flexibility exercises, and injury prevention strategies.',
                        'read_time': '8 min read',
                        'color': 'rgba(249, 115, 22, 0.1)'
                    },
                    {
                        'icon': '🩺',
                        'category': 'Preventive Care',
                        'title': 'Essential Health Screenings by Age',
                        'excerpt': 'Stay proactive with recommended health screenings and checkups. Know when to schedule blood tests, cancer screenings, and preventive examinations.',
                        'read_time': '5 min read',
                        'color': 'rgba(236, 72, 153, 0.1)'
                    },
                    {
                        'icon': '🧘',
                        'category': 'Wellness',
                        'title': 'Building a Sustainable Wellness Routine',
                        'excerpt': 'Create lasting healthy habits with realistic goal-setting and accountability systems. Balance physical health, mental wellness, and social connections.',
                        'read_time': '9 min read',
                        'color': 'rgba(6, 182, 212, 0.1)'
                    },
                    {
                        'icon': '💊',
                        'category': 'Medications',
                        'title': 'Safe Medication Management Tips',
                        'excerpt': 'Essential guidelines for storing, tracking, and taking medications safely. Avoid drug interactions, understand side effects, and communicate with your healthcare provider.',
                        'read_time': '6 min read',
                        'color': 'rgba(239, 68, 68, 0.1)'
                    },
                    {
                        'icon': '🧬',
                        'category': 'Chronic Conditions',
                        'title': 'Living Well with Diabetes',
                        'excerpt': 'Comprehensive diabetes management including blood sugar monitoring, dietary adjustments, medication adherence, and lifestyle modifications for optimal health.',
                        'read_time': '11 min read',
                        'color': 'rgba(99, 102, 241, 0.1)'
                    },
                    {
                        'icon': '🌿',
                        'category': 'Holistic Health',
                        'title': 'Natural Remedies and Alternative Medicine',
                        'excerpt': 'Explore evidence-based complementary therapies including herbal supplements, acupuncture, and integrative medicine approaches to enhance traditional treatment.',
                        'read_time': '8 min read',
                        'color': 'rgba(34, 197, 94, 0.1)'
                    }
                ]
                
                for article in articles:
                    with ui.card().style(
                        f'padding: 30px; border-radius: 16px; background: white; '
                        f'border: 2px solid rgba(102, 126, 234, 0.1); '
                        f'transition: transform 0.3s ease, box-shadow 0.3s ease; cursor: pointer;'
                    ):
                        with ui.row().classes('items-center justify-between mb-3'):
                            ui.label(article['icon']).style('font-size: 40px;')
                            with ui.card().style(
                                f'padding: 6px 14px; border-radius: 20px; background: {article["color"]};'
                            ):
                                ui.label(article['category']).style('font-size: 12px; font-weight: 600; color: #1e293b;')
                        
                        ui.label(article['title']).style(
                            'font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 12px; line-height: 1.3;'
                        )
                        
                        ui.label(article['excerpt']).style(
                            'font-size: 14px; color: #64748b; line-height: 1.6; margin-bottom: 15px;'
                        )
                        
                        ui.separator().style('margin: 15px 0;')
                        
                        with ui.row().classes('items-center justify-between'):
                            ui.label(article['read_time']).style('font-size: 13px; color: #94a3b8; font-weight: 500;')
                            ui.label('Read More →').style('font-size: 14px; color: #667eea; font-weight: 600;')
            
            # Call to Action
            with ui.column().classes('items-center text-center').style(
                'margin-top: 60px; padding: 50px; border-radius: 20px; '
                'background: white; box-shadow: 0 10px 30px rgba(0,0,0,0.08);'
            ):
                ui.label('📚').style('font-size: 56px; margin-bottom: 20px;')
                ui.label('Want More Health Tips?').style(
                    'font-size: 32px; font-weight: 700; color: #1e293b; margin-bottom: 15px;'
                )
                ui.label('Subscribe to our newsletter for weekly health insights delivered to your inbox').style(
                    'font-size: 17px; color: #64748b; margin-bottom: 30px; max-width: 600px;'
                )
                
                with ui.row().classes('items-center gap-3').style('max-width: 500px;'):
                    newsletter_email = ui.input('Your email address', placeholder='you@example.com').props('outlined rounded').classes('flex-1')
                    ui.button('Subscribe', icon='mail', on_click=lambda: ui.notify('Thanks for subscribing!', color='positive')).props('rounded').style(
                        'background: linear-gradient(45deg, #667eea, #764ba2); color: white; '
                        'padding: 12px 28px; font-weight: 600;'
                    )




@ui.page('/about')
def about_page():
    # Top Navbar - CONSISTENT ORDER
    with ui.header().classes('fixed top-0 left-0 right-0').style(
        'height: 70px; background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); '
        'box-shadow: 0 2px 10px rgba(0,0,0,0.1); z-index: 1000;'
    ):
        with ui.row().classes('w-full items-center justify-between').style('padding: 0 50px; max-width: 100%;'):
            with ui.row().classes('items-center gap-3'):
                ui.label('🏥').style('font-size: 32px;')
                ui.label('Care Bot').style(
                    'font-size: 24px; font-weight: 700; '
                    'background: linear-gradient(45deg, #667eea, #764ba2); '
                    '-webkit-background-clip: text; -webkit-text-fill-color: transparent;'
                )
            
            with ui.row().classes('gap-3'):
                ui.button('Home', on_click=lambda: ui.navigate.to('/')).props('flat').style(
                    'padding: 10px 24px; border-radius: 10px; font-weight: 600; font-size: 15px; '
                    'color: #1e293b; border: 2px solid #e2e8f0;'
                )
                ui.button('Articles', on_click=lambda: ui.navigate.to('/articles')).props('flat').style(
                    'padding: 10px 24px; border-radius: 10px; font-weight: 600; font-size: 15px; '
                    'color: #1e293b; border: 2px solid #e2e8f0;'
                )
                ui.button('Contact', on_click=lambda: ui.navigate.to('/contact')).props('flat').style(
                    'padding: 10px 24px; border-radius: 10px; font-weight: 600; font-size: 15px; '
                    'color: #1e293b; border: 2px solid #e2e8f0;'
                )
                ui.button('Login', on_click=lambda: ui.navigate.to('/login')).props('flat').style(
                    'padding: 10px 24px; border-radius: 10px; font-weight: 600; font-size: 15px; '
                    'color: #1e293b; border: 2px solid #e2e8f0;'
                )
                ui.button('Register', on_click=lambda: ui.navigate.to('/register')).props('unelevated').style(
                    'padding: 10px 24px; border-radius: 10px; font-weight: 600; font-size: 15px; '
                    'background: linear-gradient(135deg, #667eea, #764ba2); color: white; '
                    'box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);'
                )
    
    # Main Content
    with ui.column().classes('w-full').style('background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%); padding: 100px 20px 60px; min-height: 100vh;'):
        with ui.column().classes('items-center').style('max-width: 1200px; margin: 0 auto;'):
            
            # Hero Section
            with ui.column().classes('items-center text-center').style('margin-bottom: 60px;'):
                ui.label('About Care Bot').style(
                    'font-size: 48px; font-weight: 800; color: #1e293b; margin-bottom: 20px; '
                    'background: linear-gradient(45deg, #667eea, #764ba2); '
                    '-webkit-background-clip: text; -webkit-text-fill-color: transparent;'
                )
                ui.label('Your Trusted Healthcare Management Partner').style(
                    'font-size: 22px; color: #64748b; max-width: 700px; line-height: 1.6;'
                )
            
            # Mission Section
            with ui.card().style(
                'width: 100%; padding: 50px; border-radius: 20px; margin-bottom: 40px; '
                'background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)); '
                'border: 2px solid rgba(102, 126, 234, 0.2);'
            ):
                with ui.column().classes('items-center text-center'):
                    ui.label('🎯').style('font-size: 64px; margin-bottom: 20px;')
                    ui.label('Our Mission').style('font-size: 32px; font-weight: 700; color: #1e293b; margin-bottom: 15px;')
                    ui.label(
                        'We believe healthcare management should be simple, accessible, and secure. '
                        'Care Bot empowers individuals to take control of their health journey by providing '
                        'an intuitive platform to organize medical records, track health history, and generate '
                        'professional reports instantly.'
                    ).style('font-size: 18px; color: #475569; line-height: 1.8; max-width: 900px;')
            
            # What We Offer Section
            with ui.column().classes('w-full').style('margin-bottom: 40px;'):
                ui.label('What We Offer').style(
                    'font-size: 36px; font-weight: 700; color: #1e293b; text-align: center; margin-bottom: 40px;'
                )
                
                with ui.grid(columns=2).classes('gap-6 w-full'):
                    offerings = [
                        ('📝', 'Organized Records', 'Store and manage all your health records in one secure, easy-to-access location with intelligent categorization.'),
                        ('📄', 'Instant PDF Reports', 'Generate professional, shareable PDF reports of your health history anytime you need them for doctor visits.'),
                        ('🔒', 'Secure & Private', 'Your health data is protected with industry-standard security measures. We never share your information without permission.'),
                        ('🎨', 'User-Friendly Design', 'Clean, intuitive interface designed for everyone - from tech-savvy users to those who prefer simplicity.')
                    ]
                    
                    for icon, title, desc in offerings:
                        with ui.card().style(
                            'padding: 30px; border-radius: 16px; '
                            'background: white; border: 2px solid rgba(102, 126, 234, 0.1); '
                            'transition: transform 0.3s ease, box-shadow 0.3s ease;'
                        ):
                            ui.label(icon).style('font-size: 40px; margin-bottom: 15px;')
                            ui.label(title).style('font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 10px;')
                            ui.label(desc).style('font-size: 15px; color: #64748b; line-height: 1.6;')
            
            # Why Choose Us Section
            with ui.card().style(
                'width: 100%; padding: 50px; border-radius: 20px; margin-bottom: 40px; '
                'background: white; box-shadow: 0 10px 30px rgba(0,0,0,0.08);'
            ):
                ui.label('Why Choose Care Bot?').style(
                    'font-size: 32px; font-weight: 700; color: #1e293b; text-align: center; margin-bottom: 30px;'
                )
                
                with ui.column().classes('gap-4'):
                    reasons = [
                        ('✨', 'Built for Everyone', 'Whether you\'re managing chronic conditions or tracking routine checkups, Care Bot adapts to your needs.'),
                        ('⚡', 'Lightning Fast', 'Access your records instantly, generate reports in seconds, and never wait when you need your health information.'),
                        ('🌐', 'Access Anywhere', 'Use Care Bot on any device - desktop, tablet, or mobile. Your data syncs automatically across all platforms.'),
                        ('💚', 'Always Improving', 'We continuously update Care Bot with new features based on user feedback to serve you better.')
                    ]
                    
                    for icon, title, desc in reasons:
                        with ui.row().classes('items-start gap-4'):
                            ui.label(icon).style('font-size: 32px; flex-shrink: 0;')
                            with ui.column():
                                ui.label(title).style('font-size: 18px; font-weight: 700; color: #1e293b; margin-bottom: 5px;')
                                ui.label(desc).style('font-size: 15px; color: #64748b; line-height: 1.6;')
            
            # Call to Action
            with ui.column().classes('items-center text-center').style(
                'padding: 50px; border-radius: 20px; '
                'background: linear-gradient(135deg, #667eea, #764ba2);'
            ):
                ui.label('Ready to Take Control of Your Health?').style(
                    'font-size: 32px; font-weight: 700; color: white; margin-bottom: 15px;'
                )
                ui.label('Join Care Bot today and experience hassle-free healthcare management.').style(
                    'font-size: 18px; color: rgba(255, 255, 255, 0.9); margin-bottom: 30px;'
                )
                
                with ui.row().classes('gap-4'):
                    ui.button('Get Started Free', on_click=lambda: ui.navigate.to('/register')).props('unelevated').style(
                        'padding: 16px 36px; border-radius: 12px; font-weight: 700; font-size: 16px; '
                        'background: white; color: #667eea; box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);'
                    )
                    ui.button('Contact Us', on_click=lambda: ui.navigate.to('/contact')).props('outline').style(
                        'padding: 16px 36px; border-radius: 12px; font-weight: 700; font-size: 16px; '
                        'color: white; border: 2px solid white;'
                    )




@ui.page('/contact')
def contact_page():
    # Top Navbar - CONSISTENT ORDER
    with ui.header().classes('fixed top-0 left-0 right-0').style(
        'height: 70px; background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); '
        'box-shadow: 0 2px 10px rgba(0,0,0,0.1); z-index: 1000;'
    ):
        with ui.row().classes('w-full items-center justify-between').style('padding: 0 50px; max-width: 100%;'):
            with ui.row().classes('items-center gap-3'):
                ui.label('🏥').style('font-size: 32px;')
                ui.label('Care Bot').style(
                    'font-size: 24px; font-weight: 700; '
                    'background: linear-gradient(45deg, #667eea, #764ba2); '
                    '-webkit-background-clip: text; -webkit-text-fill-color: transparent;'
                )
            
            with ui.row().classes('gap-3'):
                ui.button('Home', on_click=lambda: ui.navigate.to('/')).props('flat').style(
                    'padding: 10px 24px; border-radius: 10px; font-weight: 600; font-size: 15px; '
                    'color: #1e293b; border: 2px solid #e2e8f0;'
                )
                ui.button('Articles', on_click=lambda: ui.navigate.to('/articles')).props('flat').style(
                    'padding: 10px 24px; border-radius: 10px; font-weight: 600; font-size: 15px; '
                    'color: #1e293b; border: 2px solid #e2e8f0;'
                )
                ui.button('About', on_click=lambda: ui.navigate.to('/about')).props('flat').style(
                    'padding: 10px 24px; border-radius: 10px; font-weight: 600; font-size: 15px; '
                    'color: #1e293b; border: 2px solid #e2e8f0;'
                )
                ui.button('Login', on_click=lambda: ui.navigate.to('/login')).props('flat').style(
                    'padding: 10px 24px; border-radius: 10px; font-weight: 600; font-size: 15px; '
                    'color: #1e293b; border: 2px solid #e2e8f0;'
                )
                ui.button('Register', on_click=lambda: ui.navigate.to('/register')).props('unelevated').style(
                    'padding: 10px 24px; border-radius: 10px; font-weight: 600; font-size: 15px; '
                    'background: linear-gradient(135deg, #667eea, #764ba2); color: white; '
                    'box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);'
                )
    
    # Main Content
    with ui.column().classes('w-full').style('background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%); padding: 100px 20px 60px; min-height: 100vh;'):
        with ui.column().classes('items-center').style('max-width: 1200px; margin: 0 auto;'):
            
            # Hero Section
            with ui.column().classes('items-center text-center').style('margin-bottom: 60px;'):
                ui.label('Get In Touch').style(
                    'font-size: 48px; font-weight: 800; color: #1e293b; margin-bottom: 20px; '
                    'background: linear-gradient(45deg, #667eea, #764ba2); '
                    '-webkit-background-clip: text; -webkit-text-fill-color: transparent;'
                )
                ui.label('We\'re here to help and answer any question you might have').style(
                    'font-size: 20px; color: #64748b; max-width: 700px; line-height: 1.6;'
                )
            
            with ui.row().classes('w-full gap-8').style('align-items: stretch;'):
                
                # Contact Information Card
                with ui.column().classes('gap-4').style('flex: 1;'):
                    with ui.card().style(
                        'padding: 40px; border-radius: 20px; height: 100%; '
                        'background: linear-gradient(135deg, #667eea, #764ba2); '
                        'box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);'
                    ):
                        ui.label('Contact Information').style(
                            'font-size: 28px; font-weight: 700; color: white; margin-bottom: 10px;'
                        )
                        ui.label('Fill out the form and our team will get back to you within 24 hours').style(
                            'font-size: 15px; color: rgba(255, 255, 255, 0.85); margin-bottom: 30px; line-height: 1.6;'
                        )
                        
                        # Contact Details
                        with ui.column().classes('gap-6'):
                            # Email
                            with ui.row().classes('items-start gap-4'):
                                with ui.card().style(
                                    'padding: 12px; border-radius: 12px; background: rgba(255, 255, 255, 0.15); '
                                    'backdrop-filter: blur(10px);'
                                ):
                                    ui.icon('email', size='lg').style('color: white;')
                                with ui.column():
                                    ui.label('Email Us').style('font-size: 16px; font-weight: 600; color: white; margin-bottom: 5px;')
                                    ui.label('support@carebot.com').style('font-size: 14px; color: rgba(255, 255, 255, 0.9);')
                                    ui.label('info@carebot.com').style('font-size: 14px; color: rgba(255, 255, 255, 0.9);')
                            
                            # Phone
                            with ui.row().classes('items-start gap-4'):
                                with ui.card().style(
                                    'padding: 12px; border-radius: 12px; background: rgba(255, 255, 255, 0.15); '
                                    'backdrop-filter: blur(10px);'
                                ):
                                    ui.icon('phone', size='lg').style('color: white;')
                                with ui.column():
                                    ui.label('Call Us').style('font-size: 16px; font-weight: 600; color: white; margin-bottom: 5px;')
                                    ui.label('+1 (555) 123-4567').style('font-size: 14px; color: rgba(255, 255, 255, 0.9);')
                                    ui.label('Mon-Fri 9am-6pm EST').style('font-size: 13px; color: rgba(255, 255, 255, 0.75);')
                            
                            # Location
                            with ui.row().classes('items-start gap-4'):
                                with ui.card().style(
                                    'padding: 12px; border-radius: 12px; background: rgba(255, 255, 255, 0.15); '
                                    'backdrop-filter: blur(10px);'
                                ):
                                    ui.icon('location_on', size='lg').style('color: white;')
                                with ui.column():
                                    ui.label('Visit Us').style('font-size: 16px; font-weight: 600; color: white; margin-bottom: 5px;')
                                    ui.label('123 Healthcare Ave').style('font-size: 14px; color: rgba(255, 255, 255, 0.9);')
                                    ui.label('San Francisco, CA 94102').style('font-size: 14px; color: rgba(255, 255, 255, 0.9);')
                            
                            # Working Hours
                            with ui.row().classes('items-start gap-4'):
                                with ui.card().style(
                                    'padding: 12px; border-radius: 12px; background: rgba(255, 255, 255, 0.15); '
                                    'backdrop-filter: blur(10px);'
                                ):
                                    ui.icon('schedule', size='lg').style('color: white;')
                                with ui.column():
                                    ui.label('Business Hours').style('font-size: 16px; font-weight: 600; color: white; margin-bottom: 5px;')
                                    ui.label('Monday - Friday: 9:00 AM - 6:00 PM').style('font-size: 14px; color: rgba(255, 255, 255, 0.9);')
                                    ui.label('Saturday: 10:00 AM - 4:00 PM').style('font-size: 14px; color: rgba(255, 255, 255, 0.9);')
                                    ui.label('Sunday: Closed').style('font-size: 14px; color: rgba(255, 255, 255, 0.9);')
                        
                        # Social Media
                        ui.separator().style('background: rgba(255, 255, 255, 0.2); margin: 30px 0;')
                        
                        ui.label('Connect With Us').style('font-size: 18px; font-weight: 600; color: white; margin-bottom: 15px;')
                        with ui.row().classes('gap-3'):
                            ui.button(icon='facebook').props('round flat').style('color: white; font-size: 20px;')
                            ui.button(icon='youtube_searched_for').props('round flat').style('color: white; font-size: 20px;')
                            ui.button(icon='linkedin').props('round flat').style('color: white; font-size: 20px;')
                            ui.button(icon='photo_camera').props('round flat').style('color: white; font-size: 20px;')
                
                # Contact Form Card
                with ui.column().style('flex: 1;'):
                    with ui.card().style(
                        'padding: 40px; border-radius: 20px; background: white; '
                        'box-shadow: 0 10px 30px rgba(0,0,0,0.08);'
                    ):
                        ui.label('Send Us a Message').style(
                            'font-size: 26px; font-weight: 700; color: #1e293b; margin-bottom: 25px;'
                        )
                        
                        contact_name = ui.input('Your Name', placeholder='John Doe').props('outlined rounded').classes('w-full').style('margin-bottom: 15px;')
                        contact_email = ui.input('Your Email', placeholder='john@example.com').props('type=email outlined rounded').classes('w-full').style('margin-bottom: 15px;')
                        contact_subject = ui.input('Subject', placeholder='How can we help you?').props('outlined rounded').classes('w-full').style('margin-bottom: 15px;')
                        contact_message = ui.textarea('Message', placeholder='Tell us more about your inquiry...').props('outlined rounded autogrow').classes('w-full').style('margin-bottom: 25px; min-height: 150px;')
                        
                        def send_message():
                            if not contact_name.value or not contact_email.value or not contact_message.value:
                                ui.notify('Please fill in all required fields', color='warning')
                                return
                            
                            ui.notify(f'Thank you {contact_name.value}! We\'ll get back to you soon.', color='positive')
                            contact_name.value = ''
                            contact_email.value = ''
                            contact_subject.value = ''
                            contact_message.value = ''
                        
                        ui.button('Send Message', on_click=send_message, icon='send').props('rounded').classes('w-full').style(
                            'background: linear-gradient(45deg, #667eea, #764ba2); color: white; '
                            'padding: 14px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);'
                        )
            
            # FAQ Section
            with ui.column().classes('w-full').style('margin-top: 60px;'):
                ui.label('Frequently Asked Questions').style(
                    'font-size: 36px; font-weight: 700; color: #1e293b; text-align: center; margin-bottom: 40px;'
                )
                
                with ui.grid(columns=2).classes('gap-6 w-full'):
                    faqs = [
                        ('❓', 'How secure is my health data?', 'Your data is encrypted and stored securely. We use industry-standard security protocols and never share your information without your explicit consent.'),
                        ('❓', 'Can I access my records offline?', 'Currently, Care Bot requires an internet connection. However, you can download PDF reports for offline access anytime.'),
                        ('❓', 'Is Care Bot free to use?', 'Yes! Care Bot offers a free tier with all essential features. Premium plans with additional features are available for advanced users.'),
                        ('❓', 'How do I delete my account?', 'You can request account deletion by contacting our support team. We\'ll process your request within 48 hours and permanently delete all your data.')
                    ]
                    
                    for icon, question, answer in faqs:
                        with ui.card().style(
                            'padding: 25px; border-radius: 16px; background: white; '
                            'border: 2px solid rgba(102, 126, 234, 0.1);'
                        ):
                            ui.label(icon).style('font-size: 32px; margin-bottom: 12px;')
                            ui.label(question).style('font-size: 17px; font-weight: 700; color: #1e293b; margin-bottom: 10px;')
                            ui.label(answer).style('font-size: 14px; color: #64748b; line-height: 1.6;')




@ui.page('/register')
def register_page():
    with ui.column().classes('w-full min-h-screen items-center justify-center').style(
        'background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%); padding: 20px;'
    ):
        with ui.card().style(
            'max-width: 550px; width: 100%; padding: 40px; border-radius: 20px; '
            'background: rgba(255, 255, 255, 0.95); box-shadow: 0 10px 30px rgba(0,0,0,0.1);'
        ):
            with ui.row().classes('items-center mb-4'):
                ui.icon('person_add', size='2rem').style('color: #2563eb; margin-right: 10px;')
                ui.label('Create Account').style('font-size: 28px; font-weight: 700;')
            
            ui.label('Join Care Bot to manage your health records securely').style('margin-bottom: 25px; color: #64748b;')
            
            email = ui.input('Email', placeholder='your@email.com').props('outlined rounded').classes('w-full').style('margin-bottom: 12px;')
            name = ui.input('Full Name', placeholder='John Doe').props('outlined rounded').classes('w-full').style('margin-bottom: 12px;')
            phone = ui.input('Phone Number', placeholder='+1 (555) 000-0000').props('outlined rounded').classes('w-full').style('margin-bottom: 12px;')
            
            with ui.row().classes('w-full gap-3').style('margin-bottom: 12px;'):
                age = ui.input('Age', placeholder='25').props('type=number outlined rounded').classes('flex-1')
                gender = ui.select(['Male', 'Female'], label='Gender').props('outlined rounded').classes('flex-1')
            
            password = ui.input('Password', placeholder='Strong password').props('type=password outlined rounded').classes('w-full').style('margin-bottom: 25px;')



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
                    ui.navigate.to('/login')



            with ui.row().classes('w-full gap-3'):
                ui.button('Register', on_click=submit, icon='check_circle').props('rounded').classes('flex-1').style(
                    'background: linear-gradient(45deg, #2563eb, #1d4ed8); color: white; padding: 12px; font-weight: 600;'
                )
                ui.button('Back', on_click=lambda: ui.navigate.to('/'), icon='home').props('outline rounded').style(
                    'padding: 12px 24px; font-weight: 600; color: #1e293b; border-color: #e2e8f0;'
                )
            
            with ui.row().classes('w-full justify-center mt-5'):
                ui.label('Already have an account?').style('font-size: 14px; color: #64748b;')
                ui.link('Sign in', '/login').style('font-size: 14px; color: #2563eb; margin-left: 5px; font-weight: 600;')




@ui.page('/login')
def login_page():
    with ui.column().classes('w-full min-h-screen items-center justify-center').style(
        'background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%); padding: 20px;'
    ):
        with ui.card().style(
            'max-width: 450px; width: 100%; padding: 40px; border-radius: 20px; '
            'background: rgba(255, 255, 255, 0.95); box-shadow: 0 10px 30px rgba(0,0,0,0.1);'
        ):
            with ui.row().classes('items-center mb-4'):
                ui.icon('login', size='2rem').style('color: #2563eb; margin-right: 10px;')
                ui.label('Welcome Back').style('font-size: 28px; font-weight: 700;')
            
            ui.label('Sign in to access your health dashboard').style('margin-bottom: 25px; color: #64748b;')
            
            email = ui.input('Email', placeholder='your@email.com').props('type=email outlined rounded').classes('w-full').style('margin-bottom: 15px;')
            password = ui.input('Password', placeholder='Your password').props('type=password outlined rounded').classes('w-full').style('margin-bottom: 25px;')



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



            with ui.row().classes('w-full gap-3'):
                ui.button('Login', on_click=login, icon='arrow_forward').props('rounded').classes('flex-1').style(
                    'background: linear-gradient(45deg, #2563eb, #1d4ed8); color: white; padding: 12px; font-weight: 600;'
                )
                ui.button('Back', on_click=lambda: ui.navigate.to('/'), icon='home').props('outline rounded').style(
                    'padding: 12px 24px; font-weight: 600; color: #1e293b; border-color: #e2e8f0;'
                )
            
            with ui.row().classes('w-full justify-center mt-5'):
                ui.label("Don't have an account?").style('font-size: 14px; color: #64748b;')
                ui.link('Register', '/register').style('font-size: 14px; color: #2563eb; margin-left: 5px; font-weight: 600;')




@ui.page('/health-record')
def health_record_page():
    global current_user_email
    if not current_user_email:
        with ui.column().classes('w-full min-h-screen items-center justify-center'):
            ui.icon('lock', size='4rem').style('color: #ef4444; margin-bottom: 20px;')
            ui.label("Access denied. Please log in first.").style('font-size: 20px; margin-bottom: 20px;')
            ui.button("Go to Login", on_click=lambda: ui.navigate.to('/login'), icon='login').style(
                'background: #2563eb; color: white; padding: 12px 24px; border-radius: 10px;'
            )
        return



    db: Session = SessionLocal()
    user = db.query(User).filter(User.email == current_user_email).first()
    has_records = db.query(HealthRecord).filter(HealthRecord.user_id == user.id).first() is not None
    db.close()



    with ui.column().classes('w-full min-h-screen').style(
        'background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%); padding: 20px;'
    ):
        with ui.row().classes('w-full items-center justify-between mb-5').style('max-width: 950px; margin: 0 auto;'):
            with ui.row().classes('items-center gap-2'):
                ui.icon('medical_services', size='2rem').style('color: #2563eb;')
                ui.label('Care Bot Dashboard').style('font-size: 24px; font-weight: 700;')
            
            ui.button('Logout', on_click=logout, icon='logout').props('flat').style('color: #ef4444; font-weight: 600;')
        
        with ui.row().classes('w-full gap-5').style('max-width: 950px; margin: 0 auto;'):
            with ui.column().classes('gap-4').style('flex: 0 0 260px;'):
                with ui.card().style(
                    'padding: 25px; border-radius: 16px; background: rgba(255, 255, 255, 0.95); '
                    'box-shadow: 0 4px 12px rgba(0,0,0,0.08);'
                ):
                    ui.icon('account_circle', size='3rem').style('color: #2563eb; margin-bottom: 15px;')
                    ui.label(user.name).style('font-size: 20px; font-weight: 700; margin-bottom: 5px;')
                    ui.label(user.email).style('font-size: 13px; margin-bottom: 15px; color: #64748b;')
                    ui.separator()
                    
                    if user.age:
                        with ui.row().classes('items-center gap-2 mt-3'):
                            ui.icon('cake', size='sm').style('color: #64748b;')
                            ui.label(f'Age: {user.age}').style('font-size: 14px;')
                    
                    if user.gender:
                        with ui.row().classes('items-center gap-2 mt-2'):
                            ui.icon('person', size='sm').style('color: #64748b;')
                            ui.label(f'Gender: {user.gender}').style('font-size: 14px;')
                    
                    if user.phone:
                        with ui.row().classes('items-center gap-2 mt-2'):
                            ui.icon('phone', size='sm').style('color: #64748b;')
                            ui.label(user.phone).style('font-size: 14px;')
                
                if has_records:
                    with ui.card().style(
                        'padding: 20px; border-radius: 16px; background: rgba(255, 255, 255, 0.95); '
                        'box-shadow: 0 4px 12px rgba(0,0,0,0.08);'
                    ):
                        ui.label('Last Updated').style('font-size: 13px; font-weight: 600; margin-bottom: 8px; color: #64748b;')
                        
                        time_label = ui.label(human_readable_time_diff(user.last_updated)).style('font-size: 15px; color: #10b981; margin-bottom: 15px;')
                        ui.timer(5.0, lambda: time_label.set_text(human_readable_time_diff(user.last_updated)))
                        
                        ui.separator()
                        
                        ui.button('Download PDF Report', on_click=lambda: ui.run_javascript('window.open("/download_pdf", "_blank")'), icon='download').props('rounded').classes('w-full mt-3').style(
                            'background: linear-gradient(45deg, #10b981, #059669); color: white; padding: 10px; font-weight: 600;'
                        )
            
            with ui.column().classes('flex-1'):
                with ui.card().style(
                    'padding: 35px; border-radius: 16px; background: rgba(255, 255, 255, 0.95); '
                    'box-shadow: 0 4px 12px rgba(0,0,0,0.08);'
                ):
                    with ui.row().classes('items-center mb-4'):
                        ui.icon('add_circle', size='2rem').style('color: #2563eb; margin-right: 10px;')
                        ui.label('Submit Health Record').style('font-size: 24px; font-weight: 700;')
                    
                    ui.label('Add new health information to your medical history').style('margin-bottom: 25px; color: #64748b;')
                    
                    problem_input = ui.input('Problem Name', placeholder='e.g., Annual Checkup').props('outlined rounded').classes('w-full').style('margin-bottom: 15px;')
                    summary_input = ui.textarea('Summary', placeholder='Describe symptoms, diagnosis, treatment...').props('outlined rounded autogrow').classes('w-full').style('margin-bottom: 15px; min-height: 100px;')
                    reported_date_input = ui.input('Reported On', value=datetime.now().strftime('%Y-%m-%d')).props('type=date outlined rounded').classes('w-full').style('margin-bottom: 25px;')



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



                    ui.button('Submit', on_click=submit, icon='save').props('rounded').classes('w-full').style(
                        'background: linear-gradient(45deg, #2563eb, #1d4ed8); color: white; padding: 14px; font-weight: 600; font-size: 16px;'
                    )




ui.run()
