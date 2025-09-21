# Inspector WhatsApp Integration - Implementation Roadmap

## **Project Overview**

Building a WhatsApp bot integration for the Inspector real estate platform using PyWa framework + FastAPI, with Celery/Redis for async processing.

## **Architecture Stack**

- **Framework**: FastAPI (async) + PyWa (WhatsApp Cloud API)
- **Database**: PostgreSQL (reuse Inspector's existing DB)
- **Queue**: Celery + Redis (async jobs, notifications)
- **Authentication**: JWT + OTP (extend Inspector's auth)
- **Deployment**: Docker + containerization ✅ **COMPLETED**

---

## **Phase 1: Foundation & Core Setup (Week 1-2)**

### **Milestone 1.1: Project Structure & Environment Setup**

**Duration**: 2 days
**Goal**: Get development environment running with basic FastAPI + PyWa integration

#### **Tasks:**

1. **Project Structure Setup**

   ```
   inspakta-wa/
   ├── app/
   │   ├── __init__.py
   │   ├── main.py                 # FastAPI app factory
   │   ├── config.py              # Environment configs
   │   ├── core/
   │   │   ├── __init__.py
   │   │   ├── security.py        # Auth utilities
   │   │   └── database.py        # DB connection
   │   ├── api/
   │   │   ├── __init__.py
   │   │   ├── deps.py            # Dependencies
   │   │   └── v1/
   │   │       ├── __init__.py
   │   │       ├── endpoints/
   │   │       │   ├── webhooks.py    # WhatsApp webhooks
   │   │       │   ├── auth.py        # Authentication
   │   │       │   └── health.py      # Health checks
   │   │       └── api.py
   │   ├── models/
   │   │   ├── __init__.py
   │   │   ├── user.py            # User models
   │   │   └── whatsapp.py        # WhatsApp models
   │   ├── schemas/
   │   │   ├── __init__.py
   │   │   ├── user.py            # Pydantic schemas
   │   │   └── whatsapp.py
   │   ├── services/
   │   │   ├── __init__.py
   │   │   ├── whatsapp_service.py    # WhatsApp business logic
   │   │   ├── auth_service.py        # Authentication service
   │   │   ├── notification_service.py # Notifications
   │   │   └── inspector_api.py       # Inspector backend integration
   │   ├── workers/
   │   │   ├── __init__.py
   │   │   ├── celery_app.py      # Celery configuration
   │   │   └── tasks.py           # Background tasks
   │   └── utils/
   │       ├── __init__.py
   │       ├── validators.py      # Input validation
   │       └── helpers.py         # Utility functions
   ├── tests/
   ├── docker-compose.yml
   ├── Dockerfile
   ├── requirements.txt
   ├── .env.example
   └── README.md
   ```
2. **Environment Configuration**

   ```python
   # .env.example
   # FastAPI
   DEBUG=True
   API_V1_STR=/api/v1
   PROJECT_NAME=Inspector WhatsApp Bot

   # WhatsApp Cloud API
   WHATSAPP_TOKEN=your_access_token
   WHATSAPP_PHONE_ID=your_phone_number_id
   WHATSAPP_VERIFY_TOKEN=your_verify_token
   WHATSAPP_APP_SECRET=your_app_secret

   # Database
   DATABASE_URL=postgresql://user:pass@localhost/inspakta_wa

   # Redis & Celery
   REDIS_URL=redis://localhost:6379/0
   CELERY_BROKER_URL=redis://localhost:6379/0

   # Inspector API
   INSPECTOR_API_BASE_URL=https://api.inspector.com
   INSPECTOR_API_KEY=your_inspector_api_key

   # JWT
   SECRET_KEY=your-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```
3. **Dependencies Setup**

   ```python
   # requirements.txt
   fastapi==0.104.1
   uvicorn[standard]==0.24.0
   pywa==1.15.0
   sqlalchemy==2.0.23
   alembic==1.12.1
   psycopg2-binary==2.9.7
   celery==5.3.4
   redis==5.0.1
   pydantic==2.5.0
   python-jose[cryptography]==3.3.0
   passlib[bcrypt]==1.7.4
   python-multipart==0.0.6
   httpx==0.25.2
   pytest==7.4.3
   pytest-asyncio==0.21.1
   python-dotenv==1.0.0
   ```

#### **Testing Milestone 1.1:**

- [ ] FastAPI server starts successfully
- [ ] Health check endpoint responds
- [ ] Environment variables load correctly
- [X] PyWa imports without errors

**Postman Collection**: `01-Environment-Setup.json`

- GET `/health` - Server health check
- GET `/api/v1/status` - API status

---

### **Milestone 1.2: WhatsApp Webhook Foundation**

**Duration**: 3 days
**Goal**: Establish secure WhatsApp webhook handling with verification

#### **Tasks:**

1. **Webhook Verification Setup**

   ```python
   # app/api/v1/endpoints/webhooks.py
   from fastapi import APIRouter, HTTPException, Query, Request
   from pywa import WhatsApp

   router = APIRouter()

   @router.get("/webhook")
   async def verify_webhook(
       hub_mode: str = Query(alias="hub.mode"),
       hub_challenge: str = Query(alias="hub.challenge"),
       hub_verify_token: str = Query(alias="hub.verify_token")
   ):
       """WhatsApp webhook verification"""
       if hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
           return int(hub_challenge)
       raise HTTPException(status_code=403, detail="Invalid verify token")

   @router.post("/webhook")
   async def handle_webhook(request: Request):
       """Handle incoming WhatsApp messages"""
       # Implementation will be added in next milestone
       pass
   ```
2. **PyWa Integration Setup**

   ```python
   # app/services/whatsapp_service.py
   from pywa import WhatsApp
   from pywa.types import Message, CallbackButton

   class WhatsAppService:
       def __init__(self):
           self.wa = WhatsApp(
               phone_id=settings.WHATSAPP_PHONE_ID,
               token=settings.WHATSAPP_TOKEN,
               server=None,  # We'll handle webhooks via FastAPI
               verify_token=settings.WHATSAPP_VERIFY_TOKEN,
               app_secret=settings.WHATSAPP_APP_SECRET
           )

       async def send_message(self, to: str, text: str):
           """Send text message"""
           return self.wa.send_message(to=to, text=text)

       async def send_button_message(self, to: str, text: str, buttons: list):
           """Send message with buttons"""
           return self.wa.send_message(to=to, text=text, buttons=buttons)
   ```
3. **Basic Message Handler Structure**

   ```python
   # app/core/message_handler.py
   from pywa.types import Message

   class MessageHandler:
       def __init__(self, whatsapp_service: WhatsAppService):
           self.wa_service = whatsapp_service

       async def handle_message(self, message: Message):
           """Route incoming messages based on content"""
           if message.text:
               await self._handle_text_message(message)
           elif message.button:
               await self._handle_button_click(message)

       async def _handle_text_message(self, message: Message):
           """Handle text messages"""
           # Implementation in next milestone
           pass

       async def _handle_button_click(self, message: Message):
           """Handle button clicks"""
           # Implementation in next milestone
           pass
   ```

#### **Testing Milestone 1.2:**

- [ ] Webhook verification passes Meta's validation
- [ ] Webhook can receive POST requests
- [ ] PyWa client initializes correctly
- [ ] Can send test message to WhatsApp

**Postman Collection**: `02-Webhook-Setup.json`

- GET `/api/v1/webhook?hub.mode=subscribe&hub.challenge=123&hub.verify_token=TOKEN`
- POST `/api/v1/webhook` (with sample WhatsApp payload)

**Test Commands:**

```bash
# Test webhook verification
curl "http://localhost:8000/api/v1/webhook?hub.mode=subscribe&hub.challenge=123&hub.verify_token=your_token"

# Send test message via Python
python -c "
from app.services.whatsapp_service import WhatsAppService
wa = WhatsAppService()
wa.send_message('1234567890', 'Hello from Inspector Bot!')
"
```

---

### **Milestone 1.3: Database Integration & User Models**

**Duration**: 2 days
**Goal**: Set up database models for WhatsApp users and link to Inspector accounts

#### **Tasks:**

1. **Database Models**

   ```python
   # app/models/user.py
   from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
   from sqlalchemy.ext.declarative import declarative_base
   from sqlalchemy.orm import relationship

   Base = declarative_base()

   class WhatsAppUser(Base):
       __tablename__ = "whatsapp_users"

       id = Column(Integer, primary_key=True, index=True)
       phone_number = Column(String, unique=True, index=True)
       whatsapp_name = Column(String)
       inspector_user_id = Column(Integer, ForeignKey("inspector_users.id"))
       is_linked = Column(Boolean, default=False)
       created_at = Column(DateTime, default=datetime.utcnow)
       updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

       # Relationship to Inspector user (assuming Inspector has users table)
       inspector_user = relationship("InspectorUser", back_populates="whatsapp_user")

   class InspectorUser(Base):
       __tablename__ = "inspector_users"

       id = Column(Integer, primary_key=True, index=True)
       email = Column(String, unique=True, index=True)
       role = Column(String)  # 'agent', 'seeker', 'inspector'
       phone = Column(String)

       whatsapp_user = relationship("WhatsAppUser", back_populates="inspector_user")

   class OTPVerification(Base):
       __tablename__ = "otp_verifications"

       id = Column(Integer, primary_key=True, index=True)
       phone_number = Column(String, index=True)
       email = Column(String)
       otp_code = Column(String)
       expires_at = Column(DateTime)
       verified = Column(Boolean, default=False)
       created_at = Column(DateTime, default=datetime.utcnow)
   ```
2. **Database Connection & Alembic Setup**

   ```python
   # app/core/database.py
   from sqlalchemy import create_engine
   from sqlalchemy.ext.declarative import declarative_base
   from sqlalchemy.orm import sessionmaker

   engine = create_engine(settings.DATABASE_URL)
   SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
   Base = declarative_base()

   def get_db():
       db = SessionLocal()
       try:
           yield db
       finally:
           db.close()
   ```
3. **Alembic Migration Setup**

   ```bash
   alembic init alembic
   alembic revision --autogenerate -m "Initial WhatsApp tables"
   alembic upgrade head
   ```

#### **Testing Milestone 1.3:**

- [ ] Database connection established
- [ ] Tables created successfully
- [ ] Can insert/query WhatsApp users
- [ ] Alembic migrations work

**Test Commands:**

```python
# Test database operations
from app.models.user import WhatsAppUser
from app.core.database import SessionLocal

db = SessionLocal()
user = WhatsAppUser(phone_number="1234567890", whatsapp_name="Test User")
db.add(user)
db.commit()
print(f"Created user: {user.id}")
```

---

## **Phase 2: Authentication & User Linking (Week 3-4)**

### **Milestone 2.1: OTP-Based Account Linking**

**Duration**: 4 days
**Goal**: Implement secure phone-to-Inspector account linking via OTP

#### **Tasks:**

1. **OTP Service Implementation**

   ```python
   # app/services/auth_service.py
   import random
   import string
   from datetime import datetime, timedelta

   class AuthService:
       def __init__(self, db_session, email_service, inspector_api):
           self.db = db_session
           self.email_service = email_service
           self.inspector_api = inspector_api

       async def initiate_linking(self, phone_number: str, email: str):
           """Start account linking process"""
           # Verify email exists in Inspector system
           inspector_user = await self.inspector_api.get_user_by_email(email)
           if not inspector_user:
               raise ValueError("Email not found in Inspector system")

           # Generate OTP
           otp_code = self._generate_otp()
           expires_at = datetime.utcnow() + timedelta(minutes=5)

           # Save OTP to database
           otp_record = OTPVerification(
               phone_number=phone_number,
               email=email,
               otp_code=otp_code,
               expires_at=expires_at
           )
           self.db.add(otp_record)
           self.db.commit()

           # Send OTP via email
           await self.email_service.send_otp_email(email, otp_code)

           return {"message": "OTP sent to email", "expires_in": 300}

       async def verify_otp(self, phone_number: str, otp_code: str):
           """Verify OTP and link accounts"""
           # Check OTP validity
           otp_record = self.db.query(OTPVerification).filter(
               OTPVerification.phone_number == phone_number,
               OTPVerification.otp_code == otp_code,
               OTPVerification.expires_at > datetime.utcnow(),
               OTPVerification.verified == False
           ).first()

           if not otp_record:
               raise ValueError("Invalid or expired OTP")

           # Get Inspector user
           inspector_user = await self.inspector_api.get_user_by_email(otp_record.email)

           # Create/update WhatsApp user
           wa_user = self.db.query(WhatsAppUser).filter(
               WhatsAppUser.phone_number == phone_number
           ).first()

           if not wa_user:
               wa_user = WhatsAppUser(phone_number=phone_number)
               self.db.add(wa_user)

           wa_user.inspector_user_id = inspector_user['id']
           wa_user.is_linked = True

           # Mark OTP as verified
           otp_record.verified = True

           self.db.commit()

           return {"message": "Account linked successfully", "user_role": inspector_user['role']}

       def _generate_otp(self) -> str:
           """Generate 6-digit OTP"""
           return ''.join(random.choices(string.digits, k=6))
   ```
2. **WhatsApp Authentication Flow**

   ```python
   # app/core/message_handler.py (updated)
   class MessageHandler:
       def __init__(self, whatsapp_service, auth_service, db_session):
           self.wa_service = whatsapp_service
           self.auth_service = auth_service
           self.db = db_session

       async def handle_message(self, message: Message):
           """Route messages based on user authentication status"""
           phone_number = message.from_user.wa_id

           # Check if user is already linked
           wa_user = self.db.query(WhatsAppUser).filter(
               WhatsAppUser.phone_number == phone_number,
               WhatsAppUser.is_linked == True
           ).first()

           if wa_user:
               await self._handle_authenticated_user(message, wa_user)
           else:
               await self._handle_unauthenticated_user(message)

       async def _handle_unauthenticated_user(self, message: Message):
           """Handle messages from unlinked users"""
           phone_number = message.from_user.wa_id

           if message.text and message.text.startswith('/link'):
               # Extract email from message: "/link user@example.com"
               parts = message.text.split()
               if len(parts) != 2:
                   await self.wa_service.send_message(
                       to=phone_number,
                       text="Please use format: /link your-email@example.com"
                   )
                   return

               email = parts[1]
               try:
                   result = await self.auth_service.initiate_linking(phone_number, email)
                   await self.wa_service.send_message(
                       to=phone_number,
                       text=f"OTP sent to {email}. Reply with the 6-digit code to link your account."
                   )
               except ValueError as e:
                   await self.wa_service.send_message(
                       to=phone_number,
                       text=f"Error: {str(e)}"
                   )

           elif message.text and message.text.isdigit() and len(message.text) == 6:
               # User sent OTP code
               try:
                   result = await self.auth_service.verify_otp(phone_number, message.text)
                   await self.wa_service.send_message(
                       to=phone_number,
                       text=f"✅ Account linked successfully!\nYou are registered as: {result['user_role']}"
                   )
                   # Send role-specific welcome message
                   await self._send_welcome_message(phone_number, result['user_role'])
               except ValueError as e:
                   await self.wa_service.send_message(
                       to=phone_number,
                       text=f"❌ {str(e)}\nPlease try again."
                   )

           else:
               # Send linking instructions
               await self.wa_service.send_message(
                   to=phone_number,
                   text="🏠 Welcome to Inspector!\n\nTo get started, link your account:\n\n📧 Send: /link your-email@example.com\n\n(Use the same email from your Inspector account)"
               )

       async def _send_welcome_message(self, phone_number: str, role: str):
           """Send role-specific welcome message with menu"""
           welcome_messages = {
               'agent': "🏡 **Agent Portal**\n\n• Manage property listings\n• Set inspection schedules\n• Track inquiries",
               'seeker': "🔍 **Property Seeker**\n\n• Browse available properties\n• Book inspections\n• Get notifications",
               'inspector': "📋 **Inspector Dashboard**\n\n• View assigned inspections\n• Update inspection status\n• Manage schedule"
           }

           buttons = self._get_role_menu_buttons(role)

           await self.wa_service.send_button_message(
               to=phone_number,
               text=welcome_messages.get(role, "Welcome to Inspector!"),
               buttons=buttons
           )
   ```

#### **Testing Milestone 2.1:**

- [ ] OTP generation and email sending works
- [ ] OTP verification links accounts correctly
- [ ] Authentication flow handles errors gracefully
- [ ] Role-based welcome messages display

**Postman Collection**: `03-Authentication.json`

- POST `/api/v1/auth/initiate-linking` - Start linking process
- POST `/api/v1/auth/verify-otp` - Verify OTP code

**WhatsApp Test Flow:**

1. Send: `/link test@inspector.com`
2. Check email for OTP
3. Send: `123456` (OTP code)
4. Verify account linking and role assignment

---

### **Milestone 2.2: Role-Based Menu System**

**Duration**: 3 days
**Goal**: Implement interactive menu system for each user role

#### **Tasks:**

1. **Menu Definition & Management**

   ```python
   # app/services/menu_service.py
   from pywa.types import CallbackButton

   class MenuService:
       @staticmethod
       def get_main_menu(role: str) -> list:
           """Get role-specific main menu buttons"""
           menus = {
               'agent': [
                   CallbackButton("📝 My Properties", callback_data="agent_properties"),
                   CallbackButton("📅 Set Availability", callback_data="agent_schedule"),
                   CallbackButton("📊 View Inquiries", callback_data="agent_inquiries"),
                   CallbackButton("ℹ️ Help", callback_data="help")
               ],
               'seeker': [
                   CallbackButton("🏠 Browse Properties", callback_data="seeker_browse"),
                   CallbackButton("📅 My Bookings", callback_data="seeker_bookings"),
                   CallbackButton("🔔 Notifications", callback_data="seeker_notifications"),
                   CallbackButton("ℹ️ Help", callback_data="help")
               ],
               'inspector': [
                   CallbackButton("📋 My Inspections", callback_data="inspector_inspections"),
                   CallbackButton("✅ Mark Complete", callback_data="inspector_complete"),
                   CallbackButton("📅 My Schedule", callback_data="inspector_schedule"),
                   CallbackButton("ℹ️ Help", callback_data="help")
               ]
           }
           return menus.get(role, [])

       @staticmethod
       def get_property_actions_menu() -> list:
           """Property management actions for agents"""
           return [
               CallbackButton("👁️ View Details", callback_data="property_view"),
               CallbackButton("✏️ Edit Property", callback_data="property_edit"),
               CallbackButton("📅 Set Schedule", callback_data="property_schedule"),
               CallbackButton("🔙 Back to Menu", callback_data="main_menu")
           ]

       @staticmethod
       def get_inspection_booking_menu() -> list:
           """Inspection booking options for seekers"""
           return [
               CallbackButton("📅 Available Slots", callback_data="booking_slots"),
               CallbackButton("📋 Property Details", callback_data="property_details"),
               CallbackButton("💬 Contact Agent", callback_data="contact_agent"),
               CallbackButton("🔙 Back", callback_data="seeker_browse")
           ]
   ```
2. **Button Handler Implementation**

   ```python
   # app/core/button_handler.py
   from pywa.types import CallbackButton, Message

   class ButtonHandler:
       def __init__(self, wa_service, menu_service, inspector_api, db_session):
           self.wa_service = wa_service
           self.menu_service = menu_service
           self.inspector_api = inspector_api
           self.db = db_session

       async def handle_button_click(self, message: Message):
           """Route button clicks to appropriate handlers"""
           callback_data = message.button.callback_data
           phone_number = message.from_user.wa_id

           # Get user info
           wa_user = self.db.query(WhatsAppUser).filter(
               WhatsAppUser.phone_number == phone_number
           ).first()

           if not wa_user or not wa_user.is_linked:
               await self.wa_service.send_message(
                   to=phone_number,
                   text="Please link your account first. Send: /link your-email@example.com"
               )
               return

           # Route based on callback data
           handler_map = {
               # Agent handlers
               'agent_properties': self._handle_agent_properties,
               'agent_schedule': self._handle_agent_schedule,
               'agent_inquiries': self._handle_agent_inquiries,

               # Seeker handlers
               'seeker_browse': self._handle_seeker_browse,
               'seeker_bookings': self._handle_seeker_bookings,
               'seeker_notifications': self._handle_seeker_notifications,

               # Inspector handlers
               'inspector_inspections': self._handle_inspector_inspections,
               'inspector_complete': self._handle_inspector_complete,
               'inspector_schedule': self._handle_inspector_schedule,

               # Common handlers
               'main_menu': self._handle_main_menu,
               'help': self._handle_help
           }

           handler = handler_map.get(callback_data)
           if handler:
               await handler(message, wa_user)
           else:
               await self.wa_service.send_message(
                   to=phone_number,
                   text="Feature coming soon! 🚧"
               )

       async def _handle_agent_properties(self, message: Message, wa_user: WhatsAppUser):
           """Show agent's properties"""
           phone_number = message.from_user.wa_id

           # Fetch properties from Inspector API
           properties = await self.inspector_api.get_agent_properties(wa_user.inspector_user_id)

           if not properties:
               await self.wa_service.send_message(
                   to=phone_number,
                   text="📭 No properties found.\n\nAdd properties through the Inspector website to manage them here."
               )
               return

           # Format property list
           property_text = "🏠 **Your Properties:**\n\n"
           for prop in properties[:5]:  # Limit to 5 properties
               property_text += f"🏡 {prop['title']}\n"
               property_text += f"📍 {prop['location']}\n"
               property_text += f"💰 {prop['price']}\n"
               property_text += f"Status: {prop['status']}\n\n"

           if len(properties) > 5:
               property_text += f"... and {len(properties) - 5} more properties"

           buttons = [
               CallbackButton("📊 View Analytics", callback_data="agent_analytics"),
               CallbackButton("🔙 Main Menu", callback_data="main_menu")
           ]

           await self.wa_service.send_button_message(
               to=phone_number,
               text=property_text,
               buttons=buttons
           )

       async def _handle_seeker_browse(self, message: Message, wa_user: WhatsAppUser):
           """Show available properties for seekers"""
           phone_number = message.from_user.wa_id

           # Get user preferences (could be stored in database)
           properties = await self.inspector_api.get_available_properties(
               limit=3,
               user_preferences={}  # TODO: Implement preference system
           )

           if not properties:
               await self.wa_service.send_message(
                   to=phone_number,
                   text="😔 No properties available right now.\n\nWe'll notify you when new properties are added!"
               )
               return

           for prop in properties:
               property_text = f"🏡 **{prop['title']}**\n\n"
               property_text += f"📍 {prop['location']}\n"
               property_text += f"💰 {prop['price']}\n"
               property_text += f"🛏️ {prop['bedrooms']} bed, {prop['bathrooms']} bath\n"
               property_text += f"📝 {prop['description'][:100]}..."

               buttons = [
                   CallbackButton("📅 Book Inspection", callback_data=f"book_{prop['id']}"),
                   CallbackButton("❤️ Save Property", callback_data=f"save_{prop['id']}"),
                   CallbackButton("📋 Full Details", callback_data=f"details_{prop['id']}")
               ]

               await self.wa_service.send_button_message(
                   to=phone_number,
                   text=property_text,
                   buttons=buttons
               )

       async def _handle_main_menu(self, message: Message, wa_user: WhatsAppUser):
           """Show main menu based on user role"""
           phone_number = message.from_user.wa_id

           # Get user role from Inspector API
           inspector_user = await self.inspector_api.get_user_by_id(wa_user.inspector_user_id)
           role = inspector_user['role']

           menu_buttons = self.menu_service.get_main_menu(role)

           role_emoji = {'agent': '🏡', 'seeker': '🔍', 'inspector': '📋'}
           welcome_text = f"{role_emoji.get(role, '👋')} **{role.title()} Dashboard**\n\nSelect an option:"

           await self.wa_service.send_button_message(
               to=phone_number,
               text=welcome_text,
               buttons=menu_buttons
           )
   ```

#### **Testing Milestone 2.2:**

- [ ] Role-specific menus display correctly
- [ ] Button clicks route to appropriate handlers
- [ ] Properties/inspections display from Inspector API
- [ ] Navigation between menus works smoothly

**WhatsApp Test Scenarios:**

1. Link as agent → Test property management menu
2. Link as seeker → Test property browsing
3. Link as inspector → Test inspection management
4. Test navigation: Menu → Submenu → Back to Menu

---

## **Phase 3: Core Business Logic (Week 5-6)**

### **Milestone 3.1: Property & Inspection Management**

**Duration**: 5 days
**Goal**: Implement core property browsing, inspection booking, and management features

#### **Tasks:**

1. **Inspector API Service Integration**

   ```python
   # app/services/inspector_api.py
   import httpx
   from typing import List, Dict, Optional

   class InspectorAPIService:
       def __init__(self, base_url: str, api_key: str):
           self.base_url = base_url
           self.api_key = api_key
           self.client = httpx.AsyncClient(
               base_url=base_url,
               headers={"Authorization": f"Bearer {api_key}"}
           )

       async def get_user_by_email(self, email: str) -> Optional[Dict]:
           """Get user details by email"""
           response = await self.client.get(f"/users/by-email/{email}")
           return response.json() if response.status_code == 200 else None

       async def get_user_by_id(self, user_id: int) -> Optional[Dict]:
           """Get user details by ID"""
           response = await self.client.get(f"/users/{user_id}")
           return response.json() if response.status_code == 200 else None

       async def get_agent_properties(self, agent_id: int) -> List[Dict]:
           """Get properties belonging to an agent"""
           response = await self.client.get(f"/properties/agent/{agent_id}")
           return response.json() if response.status_code == 200 else []

       async def get_available_properties(self, limit: int = 10, user_preferences: Dict = None) -> List[Dict]:
           """Get available properties for browsing"""
           params = {"limit": limit, "status": "available"}
           if user_preferences:
               params.update(user_preferences)

           response = await self.client.get("/properties", params=params)
           return response.json() if response.status_code == 200 else []

       async def get_property_details(self, property_id: int) -> Optional[Dict]:
           """Get detailed property information"""
           response = await self.client.get(f"/properties/{property_id}")
           return response.json() if response.status_code == 200 else None

       async def get_available_inspection_slots(self, property_id: int) -> List[Dict]:
           """Get available inspection time slots"""
           response = await self.client.get(f"/properties/{property_id}/inspection-slots")
           return response.json() if response.status_code == 200 else []

       async def book_inspection(self, property_id: int, seeker_id: int, slot_datetime: str) -> Dict:
           """Book an inspection slot"""
           data = {
               "property_id": property_id,
               "seeker_id": seeker_id,
               "scheduled_datetime": slot_datetime
           }
           response = await self.client.post("/inspections", json=data)
           return response.json()

       async def get_user_inspections(self, user_id: int, role: str) -> List[Dict]:
           """Get inspections for a user (different endpoints based on role)"""
           if role == 'seeker':
               endpoint = f"/inspections/seeker/{user_id}"
           elif role == 'inspector':
               endpoint = f"/inspections/inspector/{user_id}"
           elif role == 'agent':
               endpoint = f"/inspections/agent/{user_id}"
           else:
               return []

           response = await self.client.get(endpoint)
           return response.json() if response.status_code == 200 else []

       async def update_inspection_status(self, inspection_id: int, status: str, notes: str = "") -> Dict:
           """Update inspection status"""
           data = {"status": status, "notes": notes}
           response = await self.client.patch(f"/inspections/{inspection_id}", json=data)
           return response.json()
   ```
2. **Enhanced Button Handlers for Business Logic**

   ```python
   # app/core/button_handler.py (extended)

   async def _handle_book_inspection(self, message: Message, wa_user: WhatsAppUser, property_id: int):
       """Handle inspection booking flow"""
       phone_number = message.from_user.wa_id

       # Get available slots
       slots = await self.inspector_api.get_available_inspection_slots(property_id)

       if not slots:
           await self.wa_service.send_message(
               to=phone_number,
               text="😔 No inspection slots available for this property.\n\nContact the agent directly for scheduling."
           )
           return

       # Format available slots
       slots_text = "📅 **Available Inspection Slots:**\n\n"
       slot_buttons = []

       for i, slot in enumerate(slots[:5]):  # Limit to 5 slots
           slot_date = slot['datetime']
           slots_text += f"{i+1}. {slot_date}\n"
           slot_buttons.append(
               CallbackButton(
                   f"Book {slot_date}",
                   callback_data=f"confirm_booking_{property_id}_{slot['id']}"
               )
           )

       slot_buttons.append(CallbackButton("🔙 Back", callback_data="seeker_browse"))

       await self.wa_service.send_button_message(
           to=phone_number,
           text=slots_text,
           buttons=slot_buttons
       )

   async def _handle_confirm_booking(self, message: Message, wa_user: WhatsAppUser, property_id: int, slot_id: int):
       """Confirm inspection booking"""
       phone_number = message.from_user.wa_id

       try:
           # Get slot details
           property_details = await self.inspector_api.get_property_details(property_id)
           slots = await self.inspector_api.get_available_inspection_slots(property_id)
           selected_slot = next((s for s in slots if s['id'] == slot_id), None)

           if not selected_slot:
               await self.wa_service.send_message(
                   to=phone_number,
                   text="❌ Slot no longer available. Please select another time."
               )
               return

           # Book the inspection
           booking_result = await self.inspector_api.book_inspection(
               property_id=property_id,
               seeker_id=wa_user.inspector_user_id,
               slot_datetime=selected_slot['datetime']
           )

           if booking_result.get('success'):
               confirmation_text = f"✅ **Inspection Booked!**\n\n"
               confirmation_text += f"🏡 Property: {property_details['title']}\n"
               confirmation_text += f"📍 Location: {property_details['location']}\n"
               confirmation_text += f"📅 Date: {selected_slot['datetime']}\n\n"
               confirmation_text += f"📋 Booking ID: {booking_result['booking_id']}\n"
               confirmation_text += f"📞 Agent Contact: {property_details['agent_contact']}\n\n"
               confirmation_text += "We'll send you a reminder 24 hours before the inspection!"

               buttons = [
                   CallbackButton("📅 My Bookings", callback_data="seeker_bookings"),
                   CallbackButton("🏠 Browse More", callback_data="seeker_browse"),
                   CallbackButton("🔙 Main Menu", callback_data="main_menu")
               ]

               await self.wa_service.send_button_message(
                   to=phone_number,
                   text=confirmation_text,
                   buttons=buttons
               )

               # Schedule reminder task
               from app.workers.tasks import schedule_inspection_reminder
               schedule_inspection_reminder.delay(
                   booking_id=booking_result['booking_id'],
                   phone_number=phone_number,
                   inspection_datetime=selected_slot['datetime']
               )

           else:
               await self.wa_service.send_message(
                   to=phone_number,
                   text=f"❌ Booking failed: {booking_result.get('error', 'Unknown error')}"
               )

       except Exception as e:
           await self.wa_service.send_message(
               to=phone_number,
               text="❌ An error occurred while booking. Please try again."
           )

   async def _handle_seeker_bookings(self, message: Message, wa_user: WhatsAppUser):
       """Show seeker's upcoming inspections"""
       phone_number = message.from_user.wa_id

       inspections = await self.inspector_api.get_user_inspections(
           wa_user.inspector_user_id,
           'seeker'
       )

       if not inspections:
           await self.wa_service.send_message(
               to=phone_number,
               text="📭 No upcoming inspections.\n\nBrowse properties to book your first inspection!"
           )
           return

       bookings_text = "📅 **Your Upcoming Inspections:**\n\n"

       for inspection in inspections:
           bookings_text += f"🏡 {inspection['property_title']}\n"
           bookings_text += f"📍 {inspection['location']}\n"
           bookings_text += f"📅 {inspection['scheduled_datetime']}\n"
           bookings_text += f"📋 Booking ID: {inspection['id']}\n"
           bookings_text += f"Status: {inspection['status']}\n\n"

       buttons = [
           CallbackButton("📞 Contact Agents", callback_data="contact_agents"),
           CallbackButton("🏠 Browse More", callback_data="seeker_browse"),
           CallbackButton("🔙 Main Menu", callback_data="main_menu")
       ]

       await self.wa_service.send_button_message(
           to=phone_number,
           text=bookings_text,
           buttons=buttons
       )
   ```

#### **Testing Milestone 3.1:**

- [ ] Property browsing shows real data from Inspector API
- [ ] Inspection booking flow works end-to-end
- [ ] Agent can view their properties and inquiries
- [ ] Inspector can see assigned inspections
- [ ] Booking confirmations are sent correctly

**Integration Tests:**

```python
# Test property browsing
await button_handler._handle_seeker_browse(mock_message, mock_wa_user)

# Test inspection booking
await button_handler._handle_book_inspection(mock_message, mock_wa_user, property_id=123)

# Test booking confirmation
await button_handler._handle_confirm_booking(mock_message, mock_wa_user, 123, 456)
```

---

### **Milestone 3.2: Celery Background Tasks & Notifications**

**Duration**: 3 days
**Goal**: Implement async job processing for notifications and reminders

#### **Tasks:**

1. **Celery Configuration**

   ```python
   # app/workers/celery_app.py
   from celery import Celery
   from app.core.config import settings

   celery_app = Celery(
       "inspector_whatsapp",
       broker=settings.CELERY_BROKER_URL,
       backend=settings.REDIS_URL,
       include=['app.workers.tasks']
   )

   celery_app.conf.update(
       task_serializer='json',
       accept_content=['json'],
       result_serializer='json',
       timezone='UTC',
       enable_utc=True,
       beat_schedule={
           'daily-inspection-reminders': {
               'task': 'app.workers.tasks.send_daily_reminders',
               'schedule': 60.0 * 60.0 * 24,  # Daily
           },
           'property-alerts': {
               'task': 'app.workers.tasks.send_property_alerts',
               'schedule': 60.0 * 60.0 * 2,  # Every 2 hours
           },
       },
   )
   ```
2. **Background Tasks Implementation**

   ```python
   # app/workers/tasks.py
   from celery import current_task
   from datetime import datetime, timedelta
   from app.workers.celery_app import celery_app
   from app.services.whatsapp_service import WhatsAppService
   from app.services.notification_service import NotificationService
   from app.core.database import SessionLocal

   @celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
   def schedule_inspection_reminder(self, booking_id: int, phone_number: str, inspection_datetime: str):
       """Schedule inspection reminder 24 hours before"""
       try:
           inspection_time = datetime.fromisoformat(inspection_datetime)
           reminder_time = inspection_time - timedelta(hours=24)

           # Schedule the reminder task
           send_inspection_reminder.apply_async(
               args=[booking_id, phone_number],
               eta=reminder_time
           )

           return f"Reminder scheduled for {reminder_time}"

       except Exception as exc:
           current_task.retry(countdown=60, exc=exc)

   @celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
   def send_inspection_reminder(self, booking_id: int, phone_number: str):
       """Send inspection reminder message"""
       try:
           db = SessionLocal()
           wa_service = WhatsAppService()

           # Get inspection details
           inspector_api = InspectorAPIService(settings.INSPECTOR_API_BASE_URL, settings.INSPECTOR_API_KEY)
           inspection = await inspector_api.get_inspection_by_id(booking_id)

           if not inspection:
               return "Inspection not found"

           reminder_text = f"🔔 **Inspection Reminder**\n\n"
           reminder_text += f"🏡 Property: {inspection['property_title']}\n"
           reminder_text += f"📍 Location: {inspection['location']}\n"
           reminder_text += f"📅 Tomorrow at: {inspection['scheduled_datetime']}\n"
           reminder_text += f"📞 Agent: {inspection['agent_contact']}\n\n"
           reminder_text += "Don't forget to bring a valid ID!"

           buttons = [
               CallbackButton("📞 Call Agent", callback_data=f"call_{inspection['agent_id']}"),
               CallbackButton("📍 Get Directions", callback_data=f"directions_{inspection['property_id']}"),
               CallbackButton("📅 My Bookings", callback_data="seeker_bookings")
           ]

           await wa_service.send_button_message(
               to=phone_number,
               text=reminder_text,
               buttons=buttons
           )

           return "Reminder sent successfully"

       except Exception as exc:
           current_task.retry(countdown=60, exc=exc)
       finally:
           db.close()

   @celery_app.task
   def send_daily_reminders():
       """Send daily reminders for all upcoming inspections"""
       try:
           db = SessionLocal()
           tomorrow = datetime.utcnow() + timedelta(days=1)

           # Get all inspections for tomorrow
           inspector_api = InspectorAPIService(settings.INSPECTOR_API_BASE_URL, settings.INSPECTOR_API_KEY)
           inspections = inspector_api.get_inspections_by_date(tomorrow.date())

           for inspection in inspections:
               # Get WhatsApp user
               wa_user = db.query(WhatsAppUser).filter(
                   WhatsAppUser.inspector_user_id == inspection['seeker_id']
               ).first()

               if wa_user and wa_user.phone_number:
                   send_inspection_reminder.delay(
                       inspection['id'],
                       wa_user.phone_number
                   )

           return f"Scheduled {len(inspections)} reminders"

       finally:
           db.close()

   @celery_app.task
   def send_property_alerts():
       """Send new property alerts to interested seekers"""
       try:
           db = SessionLocal()
           notification_service = NotificationService(db)

           # Get new properties added in last 2 hours
           since_time = datetime.utcnow() - timedelta(hours=2)
           inspector_api = InspectorAPIService(settings.INSPECTOR_API_BASE_URL, settings.INSPECTOR_API_KEY)
           new_properties = inspector_api.get_properties_since(since_time)

           if not new_properties:
               return "No new properties"

           # Get all seekers who want notifications
           seekers = notification_service.get_seekers_with_alerts()

           wa_service = WhatsAppService()

           for seeker in seekers:
               # Filter properties based on seeker preferences
               relevant_properties = notification_service.filter_properties_for_seeker(
                   new_properties,
                   seeker
               )

               if relevant_properties:
                   await send_property_alert_to_seeker(wa_service, seeker, relevant_properties)

           return f"Sent alerts for {len(new_properties)} properties to {len(seekers)} seekers"

       finally:
           db.close()

   async def send_property_alert_to_seeker(wa_service, seeker, properties):
       """Send property alert to individual seeker"""
       alert_text = f"🏠 **New Properties Available!**\n\n"

       for prop in properties[:3]:  # Limit to 3 properties per alert
           alert_text += f"🏡 {prop['title']}\n"
           alert_text += f"📍 {prop['location']}\n"
           alert_text += f"💰 {prop['price']}\n\n"

       if len(properties) > 3:
           alert_text += f"...and {len(properties) - 3} more properties!"

       buttons = [
           CallbackButton("🔍 Browse All", callback_data="seeker_browse"),
           CallbackButton("🔕 Stop Alerts", callback_data="disable_alerts")
       ]

       await wa_service.send_button_message(
           to=seeker['phone_number'],
           text=alert_text,
           buttons=buttons
       )
   ```
3. **Notification Service**

   ```python
   # app/services/notification_service.py
   from sqlalchemy.orm import Session
   from app.models.user import WhatsAppUser

   class NotificationService:
       def __init__(self, db_session: Session):
           self.db = db_session

       def get_seekers_with_alerts(self):
           """Get all seekers who have enabled property alerts"""
           seekers = self.db.query(WhatsAppUser).join(
               # Join with Inspector users table where role = 'seeker' and alerts_enabled = True
           ).all()
           return seekers

       def filter_properties_for_seeker(self, properties, seeker):
           """Filter properties based on seeker preferences"""
           # TODO: Implement preference-based filtering
           # For now, return all properties
           return properties

       def update_alert_preferences(self, wa_user_id: int, enabled: bool):
           """Update seeker's alert preferences"""
           # TODO: Implement alert preference management
           pass
   ```

#### **Testing Milestone 3.2:**

- [ ] Celery workers start successfully
- [ ] Inspection reminders are scheduled and sent
- [ ] Daily reminder task processes all inspections
- [ ] Property alerts are sent to relevant seekers
- [ ] Task retries work on failures

**Test Commands:**

```bash
# Start Celery worker
celery -A app.workers.celery_app worker --loglevel=info

# Start Celery beat scheduler
celery -A app.workers.celery_app beat --loglevel=info

# Test individual tasks
python -c "
from app.workers.tasks import schedule_inspection_reminder
result = schedule_inspection_reminder.delay(123, '1234567890', '2024-01-15T10:00:00')
print(result.get())
"
```

---

## **Phase 4: Production Readiness (Week 7-8)**

### **Milestone 4.1: Error Handling, Logging & Monitoring**

**Duration**: 3 days
**Goal**: Implement comprehensive error handling, logging, and monitoring

#### **Tasks:**

1. **Centralized Error Handling**

   ```python
   # app/core/exceptions.py
   from fastapi import HTTPException

   class InspectorAPIError(Exception):
       """Custom exception for Inspector API errors"""
       def __init__(self, message: str, status_code: int = 500):
           self.message = message
           self.status_code = status_code
           super().__init__(self.message)

   class WhatsAppUserNotLinkedError(Exception):
       """Exception for unlinked WhatsApp users"""
       pass

   class OTPExpiredError(Exception):
       """Exception for expired OTP codes"""
       pass

   # app/core/error_handlers.py
   import logging
   from fastapi import Request, HTTPException
   from fastapi.responses import JSONResponse

   logger = logging.getLogger(__name__)

   async def inspector_api_error_handler(request: Request, exc: InspectorAPIError):
       """Handle Inspector API errors"""
       logger.error(f"Inspector API Error: {exc.message}")
       return JSONResponse(
           status_code=exc.status_code,
           content={"detail": exc.message, "type": "inspector_api_error"}
       )

   async def whatsapp_error_handler(request: Request, exc: Exception):
       """Handle WhatsApp-related errors"""
       logger.error(f"WhatsApp Error: {str(exc)}")
       return JSONResponse(
           status_code=500,
           content={"detail": "WhatsApp service error", "type": "whatsapp_error"}
       )
   ```
2. **Comprehensive Logging Setup**

   ```python
   # app/core/logging_config.py
   import logging
   import sys
   from logging.handlers import RotatingFileHandler
   from pathlib import Path

   def setup_logging():
       """Configure application logging"""

       # Create logs directory
       log_dir = Path("logs")
       log_dir.mkdir(exist_ok=True)

       # Configure formatters
       detailed_formatter = logging.Formatter(
           '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
       )

       simple_formatter = logging.Formatter(
           '%(asctime)s - %(levelname)s - %(message)s'
       )

       # Configure root logger
       root_logger = logging.getLogger()
       root_logger.setLevel(logging.INFO)

       # Console handler
       console_handler = logging.StreamHandler(sys.stdout)
       console_handler.setFormatter(simple_formatter)
       console_handler.setLevel(logging.INFO)
       root_logger.addHandler(console_handler)

       # File handler for all logs
       file_handler = RotatingFileHandler(
           log_dir / "app.log",
           maxBytes=10*1024*1024,  # 10MB
           backupCount=5
       )
       file_handler.setFormatter(detailed_formatter)
       file_handler.setLevel(logging.INFO)
       root_logger.addHandler(file_handler)

       # Separate error log
       error_handler = RotatingFileHandler(
           log_dir / "errors.log",
           maxBytes=10*1024*1024,  # 10MB
           backupCount=5
       )
       error_handler.setFormatter(detailed_formatter)
       error_handler.setLevel(logging.ERROR)
       root_logger.addHandler(error_handler)

       # WhatsApp-specific logger
       whatsapp_logger = logging.getLogger("whatsapp")
       whatsapp_handler = RotatingFileHandler(
           log_dir / "whatsapp.log",
           maxBytes=5*1024*1024,  # 5MB
           backupCount=3
       )
       whatsapp_handler.setFormatter(detailed_formatter)
       whatsapp_logger.addHandler(whatsapp_handler)
       whatsapp_logger.setLevel(logging.INFO)
   ```
3. **Enhanced Message Handler with Error Handling**

   ```python
   # app/core/message_handler.py (enhanced)
   import logging
   from typing import Optional

   logger = logging.getLogger("whatsapp")

   class MessageHandler:
       def __init__(self, wa_service, auth_service, db_session):
           self.wa_service = wa_service
           self.auth_service = auth_service
           self.db = db_session

       async def handle_message(self, message: Message) -> Optional[str]:
           """Handle incoming message with comprehensive error handling"""
           phone_number = message.from_user.wa_id

           try:
               logger.info(f"Received message from {phone_number}: {message.text[:50]}...")

               # Check if user is linked
               wa_user = self.db.query(WhatsAppUser).filter(
                   WhatsAppUser.phone_number == phone_number,
                   WhatsAppUser.is_linked == True
               ).first()

               if wa_user:
                   await self._handle_authenticated_user(message, wa_user)
               else:
                   await self._handle_unauthenticated_user(message)

               logger.info(f"Message processed successfully for {phone_number}")
               return "success"

           except WhatsAppUserNotLinkedError:
               logger.warning(f"Unlinked user attempted action: {phone_number}")
               await self._send_linking_instructions(phone_number)

           except OTPExpiredError:
               logger.warning(f"Expired OTP attempt from {phone_number}")
               await self.wa_service.send_message(
                   to=phone_number,
                   text="🕐 OTP expired. Please request a new one by sending: /link your-email@example.com"
               )

           except InspectorAPIError as e:
               logger.error(f"Inspector API error for {phone_number}: {e.message}")
               await self.wa_service.send_message(
                   to=phone_number,
                   text="⚠️ Service temporarily unavailable. Please try again in a few minutes."
               )

           except Exception as e:
               logger.error(f"Unexpected error handling message from {phone_number}: {str(e)}", exc_info=True)
               await self.wa_service.send_message(
                   to=phone_number,
                   text="❌ An unexpected error occurred. Our team has been notified."
               )

               # Send alert to admin (implement notification to dev team)
               await self._send_admin_alert(f"WhatsApp Bot Error: {str(e)}", phone_number)

           return "error"

       async def _send_admin_alert(self, error_message: str, user_phone: str):
           """Send alert to admin about critical errors"""
           # TODO: Implement admin notification (email, Slack, etc.)
           logger.critical(f"ADMIN ALERT: {error_message} | User: {user_phone}")

       async def _handle_authenticated_user(self, message: Message, wa_user: WhatsAppUser):
           """Handle messages from authenticated users with error boundaries"""
           try:
               if message.text:
                   await self._handle_text_message(message, wa_user)
               elif message.button:
                   await self._handle_button_click(message, wa_user)
               else:
                   await self.wa_service.send_message(
                       to=message.from_user.wa_id,
                       text="🤔 I can only handle text messages and button clicks for now."
                   )

           except Exception as e:
               logger.error(f"Error in authenticated user flow: {str(e)}")
               raise  # Re-raise to be caught by main handler
   ```

#### **Testing Milestone 4.1:**

- [ ] Error handlers catch and log exceptions appropriately
- [ ] Different log levels are written to correct files
- [ ] Admin alerts are triggered for critical errors
- [ ] Users receive helpful error messages
- [ ] Logs contain sufficient debugging information

**Test Error Scenarios:**

```python
# Test OTP expiration
# Test Inspector API failure
# Test database connection loss
# Test WhatsApp API rate limiting
# Test malformed webhook data
```

---

### **Milestone 4.2: Security Hardening & Validation**

**Duration**: 2 days
**Goal**: Implement security best practices and input validation

#### **Tasks:**

1. **Webhook Security Implementation**

   ```python
   # app/core/security.py
   import hmac
   import hashlib
   from fastapi import HTTPException, Request

   async def verify_webhook_signature(request: Request, app_secret: str):
       """Verify WhatsApp webhook signature"""
       signature = request.headers.get("X-Hub-Signature-256")
       if not signature:
           raise HTTPException(status_code=403, detail="Missing signature")

       body = await request.body()
       expected_signature = "sha256=" + hmac.new(
           app_secret.encode(),
           body,
           hashlib.sha256
       ).hexdigest()

       if not hmac.compare_digest(signature, expected_signature):
           raise HTTPException(status_code=403, detail="Invalid signature")

       return True

   def validate_phone_number(phone: str) -> bool:
       """Validate phone number format"""
       import re
       # Basic validation for international format
       pattern = r'^\+?[1-9]\d{1,14}$'
       return bool(re.match(pattern, phone))

   def sanitize_message_text(text: str) -> str:
       """Sanitize user input text"""
       if not text:
           return ""

       # Remove potential harmful characters
       import html
       sanitized = html.escape(text)

       # Limit length
       max_length = 1000
       if len(sanitized) > max_length:
           sanitized = sanitized[:max_length] + "..."

       return sanitized
   ```
2. **Rate Limiting Implementation**

   ```python
   # app/core/rate_limiter.py
   import time
   from typing import Dict, Tuple
   import redis

   class RateLimiter:
       def __init__(self, redis_client: redis.Redis):
           self.redis = redis_client

       async def is_allowed(self, key: str, limit: int, window: int) -> Tuple[bool, int]:
           """
           Check if request is allowed under rate limit

           Args:
               key: Unique identifier (e.g., phone number)
               limit: Maximum requests allowed
               window: Time window in seconds

           Returns:
               (is_allowed, remaining_requests)
           """
           current_time = int(time.time())
           pipeline = self.redis.pipeline()

           # Remove expired entries
           pipeline.zremrangebyscore(key, 0, current_time - window)

           # Count current requests
           pipeline.zcard(key)

           # Add current request
           pipeline.zadd(key, {str(current_time): current_time})

           # Set expiry
           pipeline.expire(key, window)

           results = pipeline.execute()
           current_requests = results[1]

           if current_requests >= limit:
               return False, 0

           return True, limit - current_requests - 1

       async def check_message_rate_limit(self, phone_number: str) -> bool:
           """Check message rate limit (10 messages per minute)"""
           allowed, remaining = await self.is_allowed(
               f"msg_rate:{phone_number}",
               limit=10,
               window=60
           )
           return allowed

       async def check_otp_rate_limit(self, phone_number: str) -> bool:
           """Check OTP request rate limit (3 OTPs per hour)"""
           allowed, remaining = await self.is_allowed(
               f"otp_rate:{phone_number}",
               limit=3,
               window=3600
           )
           return allowed
   ```
3. **Input Validation Schemas**

   ```python
   # app/schemas/validation.py
   from pydantic import BaseModel, validator
   from typing import Optional

   class WebhookMessage(BaseModel):
       """Validate incoming webhook messages"""
       object: str
       entry: list

       @validator('object')
       def validate_object_type(cls, v):
           if v != 'whatsapp_business_account':
               raise ValueError('Invalid webhook object type')
           return v

   class LinkAccountRequest(BaseModel):
       """Validate account linking requests"""
       phone_number: str
       email: str

       @validator('phone_number')
       def validate_phone(cls, v):
           if not validate_phone_number(v):
               raise ValueError('Invalid phone number format')
           return v

       @validator('email')
       def validate_email(cls, v):
           import re
           email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
           if not re.match(email_pattern, v):
               raise ValueError('Invalid email format')
           return v

   class OTPVerification(BaseModel):
       """Validate OTP verification"""
       phone_number: str
       otp_code: str

       @validator('otp_code')
       def validate_otp_format(cls, v):
           if not v.isdigit() or len(v) != 6:
               raise ValueError('OTP must be 6 digits')
           return v
   ```

#### **Testing Milestone 4.2:**

- [ ] Webhook signature verification works correctly
- [ ] Rate limiting prevents abuse
- [ ] Input validation rejects malformed data
- [ ] Phone number validation accepts valid formats
- [ ] Security headers are set appropriately

**Security Test Scenarios:**

```bash
# Test webhook signature verification
curl -X POST http://localhost:8000/api/v1/webhook \
  -H "X-Hub-Signature-256: sha256=invalid" \
  -d '{"test": "data"}'

# Test rate limiting
for i in {1..15}; do
  curl -X POST http://localhost:8000/api/v1/webhook -d "{\"test\": \"$i\"}"
done
```

---

### **Milestone 4.3: Docker Deployment & Documentation**

**Duration**: 3 days
**Goal**: Containerize application and create deployment documentation

#### **Tasks:**

1. **Dockerfile & Docker Compose**

   ```dockerfile
   # Dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       gcc \
       postgresql-client \
       && rm -rf /var/lib/apt/lists/*

   # Copy requirements and install Python dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   # Copy application code
   COPY . .

   # Create non-root user
   RUN useradd --create-home --shell /bin/bash app \
       && chown -R app:app /app
   USER app

   # Expose port
   EXPOSE 8000

   # Health check
   HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
       CMD curl -f http://localhost:8000/health || exit 1

   # Start command
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

   ```yaml
   # docker-compose.yml
   version: '3.8'

   services:
     app:
       build: .
       ports:
         - "8000:8000"
       environment:
         - DATABASE_URL=postgresql://postgres:password@db:5432/inspakta_wa
         - REDIS_URL=redis://redis:6379/0
         - CELERY_BROKER_URL=redis://redis:6379/0
       depends_on:
         - db
         - redis
       volumes:
         - ./logs:/app/logs
       restart: unless-stopped
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
         interval: 30s
         timeout: 10s
         retries: 3

     celery-worker:
       build: .
       command: celery -A app.workers.celery_app worker --loglevel=info
       environment:
         - DATABASE_URL=postgresql://postgres:password@db:5432/inspakta_wa
         - REDIS_URL=redis://redis:6379/0
         - CELERY_BROKER_URL=redis://redis:6379/0
       depends_on:
         - db
         - redis
       volumes:
         - ./logs:/app/logs
       restart: unless-stopped

     celery-beat:
       build: .
       command: celery -A app.workers.celery_app beat --loglevel=info
       environment:
         - DATABASE_URL=postgresql://postgres:password@db:5432/inspakta_wa
         - REDIS_URL=redis://redis:6379/0
         - CELERY_BROKER_URL=redis://redis:6379/0
       depends_on:
         - db
         - redis
       volumes:
         - ./logs:/app/logs
       restart: unless-stopped

     db:
       image: postgres:15
       environment:
         - POSTGRES_DB=inspakta_wa
         - POSTGRES_USER=postgres
         - POSTGRES_PASSWORD=password
       volumes:
         - postgres_data:/var/lib/postgresql/data
         - ./init.sql:/docker-entrypoint-initdb.d/init.sql
       ports:
         - "5432:5432"
       restart: unless-stopped

     redis:
       image: redis:7-alpine
       ports:
         - "6379:6379"
       volumes:
         - redis_data:/data
       restart: unless-stopped

   volumes:
     postgres_data:
     redis_data:
   ```
2. **Production Deployment Guide**

   ```markdown
   # DEPLOYMENT.md

   ## Production Deployment Guide

   ### Prerequisites
   - Docker & Docker Compose installed
   - WhatsApp Business Account with Cloud API access
   - PostgreSQL database (or use Docker)
   - Redis instance (or use Docker)
   - Domain name with SSL certificate
   - Inspector API credentials

   ### Environment Setup

   1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd inspakta-wa
   ```

   2. **Configure Environment**

   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

   3. **Required Environment Variables**

   ```bash
   # WhatsApp Configuration
   WHATSAPP_TOKEN=your_permanent_token
   WHATSAPP_PHONE_ID=your_phone_number_id
   WHATSAPP_VERIFY_TOKEN=your_custom_verify_token
   WHATSAPP_APP_SECRET=your_app_secret

   # Database
   DATABASE_URL=postgresql://user:pass@host:5432/dbname

   # Redis
   REDIS_URL=redis://host:6379/0
   CELERY_BROKER_URL=redis://host:6379/0

   # Inspector API
   INSPECTOR_API_BASE_URL=https://api.inspector.com
   INSPECTOR_API_KEY=your_api_key

   # Security
   SECRET_KEY=your-super-secret-key-here
   ```

   ### Deployment Steps


   1. **Build and Start Services**

   ```bash
   docker-compose up -d
   ```

   2. **Run Database Migrations**

   ```bash
   docker-compose exec app alembic upgrade head
   ```

   3. **Verify Health**

   ```bash
   curl http://your-domain.com/health
   ```

   ### WhatsApp Webhook Configuration

   1. **Set Webhook URL**

   ```bash
   curl -X POST "https://graph.facebook.com/v18.0/{phone-number-id}/webhooks" \
     -H "Authorization: Bearer {access-token}" \
     -H "Content-Type: application/json" \
     -d '{
       "webhooks_url": "https://your-domain.com/api/v1/webhook",
       "verify_token": "your_verify_token"
     }'
   ```

   2. **Subscribe to Webhook Fields**

   ```bash
   curl -X POST "https://graph.facebook.com/v18.0/{whatsapp-business-account-id}/subscriptions" \
     -H "Authorization: Bearer {access-token}" \
     -H "Content-Type: application/json" \
     -d '{
       "object": "whatsapp_business_account",
       "callback_url": "https://your-domain.com/api/v1/webhook",
       "verify_token": "your_verify_token",
       "fields": ["messages"]
     }'
   ```

   ### Monitoring & Maintenance

   1. **View Logs**

   ```bash
   docker-compose logs -f app
   docker-compose logs -f celery-worker
   ```

   2. **Health Checks**

   ```bash
   curl http://your-domain.com/health
   curl http://your-domain.com/api/v1/status
   ```

   3. **Scaling Workers**

   ```bash
   docker-compose up -d --scale celery-worker=3
   ```

   ### Backup & Recovery

   1. **Database Backup**

   ```bash
   docker-compose exec db pg_dump -U postgres inspakta_wa > backup.sql
   ```

   2. **Redis Backup**

   ```bash
   docker-compose exec redis redis-cli BGSAVE
   ```

   ```

   ```
3. **API Documentation Updates**

   ```python
   # app/main.py (enhanced)
   from fastapi import FastAPI
   from fastapi.middleware.cors import CORSMiddleware
   from fastapi.openapi.docs import get_swagger_ui_html
   from fastapi.openapi.utils import get_openapi

   app = FastAPI(
       title="Inspector WhatsApp Bot API",
       description="""
       WhatsApp integration for Inspector real estate platform.

       ## Features
       - WhatsApp Cloud API integration
       - User authentication via OTP
       - Role-based interactions (Agents, Seekers, Inspectors)
       - Property browsing and inspection booking
       - Automated notifications and reminders

       ## Authentication
       All webhook endpoints use signature verification.
       User interactions require account linking via OTP.
       """,
       version="1.0.0",
       docs_url="/docs",
       redoc_url="/redoc"
   )

   def custom_openapi():
       if app.openapi_schema:
           return app.openapi_schema

       openapi_schema = get_openapi(
           title="Inspector WhatsApp Bot",
           version="1.0.0",
           description="WhatsApp integration for Inspector real estate platform",
           routes=app.routes,
       )

       # Add webhook signature security scheme
       openapi_schema["components"]["securitySchemes"] = {
           "WebhookSignature": {
               "type": "apiKey",
               "in": "header",
               "name": "X-Hub-Signature-256"
           }
       }

       app.openapi_schema = openapi_schema
       return app.openapi_schema

   app.openapi = custom_openapi
   ```

#### **Testing Milestone 4.3:**

- [ ] Docker containers build and start successfully
- [ ] All services communicate correctly in Docker environment
- [ ] Health checks pass in containerized setup
- [ ] Database migrations run in Docker
- [ ] API documentation is comprehensive and accurate

**Deployment Verification:**

```bash
# Test complete deployment
docker-compose up -d
docker-compose ps
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

---

## **Final Testing & Launch Checklist**

### **End-to-End Testing Scenarios**

1. **New User Onboarding**

   - [ ] User sends first message to bot
   - [ ] Linking flow works with valid email
   - [ ] OTP sent and verified successfully
   - [ ] Role-based welcome message displays
   - [ ] Main menu functions correctly
2. **Seeker User Journey**

   - [ ] Browse available properties
   - [ ] View property details
   - [ ] Book inspection slot
   - [ ] Receive booking confirmation
   - [ ] Get 24-hour reminder
   - [ ] View booking history
3. **Agent User Journey**

   - [ ] View property listings
   - [ ] See inspection inquiries
   - [ ] Set availability status
   - [ ] Receive booking notifications
4. **Inspector User Journey**

   - [ ] View assigned inspections
   - [ ] Update inspection status
   - [ ] Confirm completions
5. **Error Handling**

   - [ ] Invalid OTP attempts
   - [ ] Expired OTP handling
   - [ ] Inspector API failures
   - [ ] Rate limiting enforcement
   - [ ] Malformed webhook data

### **Production Readiness Checklist**

- [ ] All environment variables configured
- [ ] Webhook signature verification active
- [ ] Rate limiting implemented
- [ ] Comprehensive logging setup
- [ ] Error monitoring alerts configured
- [ ] Database backup strategy implemented
- [ ] SSL certificates installed
- [ ] Load balancing configured (if needed)
- [ ] Monitoring dashboards setup
- [ ] Documentation complete and accurate

### **Performance Benchmarks**

- [ ] Webhook response time < 500ms
- [ ] Message delivery success rate > 99%
- [ ] Database query performance optimized
- [ ] Celery task processing efficiency
- [ ] Memory usage within acceptable limits
- [ ] CPU utilization under load

---

## **Postman Collections Structure**

### **Collection 1: Environment Setup**

- GET `/health` - Basic health check
- GET `/api/v1/status` - API status and version

### **Collection 2: Webhook Testing**

- GET `/api/v1/webhook` - Webhook verification
- POST `/api/v1/webhook` - Message webhook (with signatures)

### **Collection 3: Authentication Flow**

- POST `/api/v1/auth/initiate-linking` - Start linking
- POST `/api/v1/auth/verify-otp` - Complete linking

### **Collection 4: Inspector API Integration**

- GET `/api/v1/properties` - Property listings
- GET `/api/v1/inspections/{user_id}` - User inspections
- POST `/api/v1/inspections` - Book inspection

### **Collection 5: Admin & Monitoring**

- GET `/api/v1/metrics` - Application metrics
- GET `/api/v1/users/stats` - User statistics
- POST `/api/v1/admin/broadcast` - Admin broadcast message

This roadmap provides a comprehensive, testable path to building a production-ready WhatsApp integration for Inspector using modern best practices and scalable architecture.
