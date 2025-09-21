I**nspector WhatsApp Integration – Technical Requirements Document (TRD)**

## **1. Overview**

Inspector is an existing real estate platform that allows agents, inspectors, and seekers to manage property listings and inspections.

The goal of this project is to **extend Inspector’s functionality into WhatsApp** so users can interact more easily without always logging into the website.

* **WhatsApp Bot MVP:** Agents upload properties, seekers book inspections, inspectors manage schedules.
* **Notifications:** Users linked via phone number receive inspection updates and property alerts directly in WhatsApp.
* **AI Assistant (Future):** Conversational support to handle free-text queries, beyond button-based workflows.

This integration **does not replace the website** but complements it, leveraging existing services (auth, DB, email).

---

## **2. Scope**

### **In-Scope**

* WhatsApp bot integration (structured menu flows + notifications).
* Linking WhatsApp accounts to existing Inspector accounts (via phone + OTP/email verification).
* Sync with existing database and backend APIs.
* Queue and job handling for message delivery and inspection notifications.
* Optional group integration: if users click property links in WhatsApp groups, they can be redirected to the Inspector website for full details.

### **Out-of-Scope**

* Rebuilding authentication, database, or email services (already exist in Inspector).
* Creating a standalone real estate system separate from Inspector.

---

## **3. Core Components**

### **3.1 Backend & Integration**

* **Framework:** FastAPI (Python)
* **Queue / Async Jobs:** Celery + Redis (for WhatsApp messages, notifications, reminders)
* **WhatsApp API:** Meta WhatsApp Cloud API (preferred for cost + flexibility)
* **Email Service:** Use Inspector’s existing setup (e.g., SendGrid/SES)
* **Authentication:** Reuse Inspector’s existing auth service; extend it for WhatsApp linking

### **3.2 Reuse from Inspector**

* **Database:** Use Inspector’s DB via existing backend APIs
* **Authentication:** Extend existing JWT/OTP auth, add WhatsApp phone linking flow
* **Email Service:** Already available for OTP and notifications

---

## **4. User Roles & Flows**

### **Agents**

* Post new property via website (core flow).
* Receive WhatsApp confirmation once property is live.
* Set availability (status) and inspection slots from WhatsApp menus.
* Get notified when seekers show interest in their property.

### **Inspectors**

* Assigned/registered by admin (existing flow).
* Receive WhatsApp updates on inspections assigned to them.
* Confirm inspection completion via WhatsApp bot.

### **Seekers**

* Sign up on website first (account creation flow unchanged).
* Link their WhatsApp number (via OTP verification).
* Receive notifications on property availability & inspection schedules.
* Book inspection slots directly from WhatsApp.
* Get reminders via WhatsApp + email.

---

## **5. WhatsApp Bot Flows**

* **Authentication on WhatsApp:**
  1. User messages Inspector WhatsApp line.
  2. Bot checks DB for linked phone number.
  3. If unlinked → bot requests email → OTP sent via existing email service → user enters OTP → account linked.
* **Menu-Driven Interaction (MVP):**
  * **Agents:** “Press 1 to mark property available/unavailable, 2 to set inspection date…”
  * **Seekers:** “Press 1 to see inspection schedule, 2 to book inspection, 3 to see interested properties…”
  * **Inspectors:** “Press 1 to view assigned inspections, 2 to confirm completion…”
* **AI Chat (Phase 2):**
  * Users ask natural questions like “What 3-bedroom apartments are available in Lekki next week?”
  * Bot integrates with Inspector APIs to fetch structured answers.

---

## **6. AI Chat Assistant (Future Phase)**

* **Frameworks:** LangChain or LlamaIndex for DB-context retrieval
* **LLM Backend:** OpenAI GPT-4/5 or local model (LLaMA/Anthropic Claude)
* **Integration:** Middleware on FastAPI calling Inspector APIs before responding
* **Fallback:** If user query doesn’t match structured menu, AI handles it

---

## **7. Backend Design**

### **Services**

1. **WhatsApp Service:** Handles inbound/outbound messages via Cloud API.
2. **Linking Service:** Links WhatsApp phone → Inspector account via OTP.
3. **Notification Service:** Dispatches reminders/updates (WhatsApp + Email).
4. **Queue Service:** Manages scheduled jobs (e.g., inspection reminders).
5. **AI Service (Future):** Fetches structured data + enriches responses with LLM.

### **Suggested Packages**

* **fastapi** – Web framework
* **sqlalchemy** – ORM (reuse existing models if available)
* **celery** + **redis** – Task scheduling, background jobs
* **pyjwt** – Token management (if needed for WhatsApp linking)
* **httpx** or **requests** – WhatsApp Cloud API calls
* **langchain** / **llama-index** – AI orchestration (future)

---

## **8. Deployment**

* **Backend Hosting:** Reuse Inspector’s infra (or deploy separately on Koyeb/Render).
* **WhatsApp API:** Meta Cloud API (primary channel).
* **Redis + Celery:** Could be deployed as add-ons to Inspector infra.

---

## **9. Timeline (WhatsApp MVP)**

* **Week 1–2:** FastAPI WhatsApp service + account linking flow
* **Week 3–4:** Agent & seeker flows (availability, inspection booking)
* **Week 5–6:** Inspector flows + reminders
* **Week 7:** Queue & async jobs (notifications, reminders)
* **Week 8:** QA + integration with live Inspector backend

**Phase 2 (AI Assistant):** Planned +4 weeks after MVP release
