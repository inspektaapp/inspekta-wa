# WhatsApp Business API Setup Guide

## Quick Start with Meta for Developers (FREE)

### Step 1: Create Meta Developer Account

1. Visit https://developers.facebook.com/
2. Click "Get Started" and login with Facebook
3. Click "Create App" → "Business" → Continue
4. Enter app name: "Inspector WhatsApp Bot"

### Step 2: Add WhatsApp Product

1. In your app dashboard, click "Add Product"
2. Find "WhatsApp Business API" and click "Set Up"
3. Complete the setup wizard

### Step 3: Get Your Credentials

#### Phone Number ID

- Go to WhatsApp → API Setup
- Copy the "Phone number ID" (looks like: 123456789012345)

#### Access Token

- In the same section, copy the "Temporary access token"
- For production, you'll generate a permanent token

#### App Secret

- Go to Settings → Basic
- Copy "App Secret" (click "Show")

#### Verify Token

- Create your own random string (e.g., "inspector_verify_2024_xyz")

### Step 4: Configure Your Environment

Create/update your `.env` file:

```bash
# WhatsApp Business API Credentials
WHATSAPP_PHONE_ID=123456789012345  # Your Phone Number ID
WHATSAPP_TOKEN=EAAxxxxxxxxxxxxx   # Your Access Token
WHATSAPP_VERIFY_TOKEN=inspector_verify_2024_xyz  # Your chosen verify token
WHATSAPP_APP_SECRET=abcd1234567890  # Your App Secret

# Other settings remain the same...
```

### Step 5: Test Your Setup

1. Start your application:

   ```bash
   python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
2. Check webhook status:

   ```bash
   curl http://localhost:8000/api/v1/whatsapp/webhook/status
   ```
3. You should see `"webhook_configured": true`

### Step 6: Set Up Webhook URL (Production)

For production, you need a public HTTPS URL. Options:

#### Option A: ngrok (Quick Testing)

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com/

# Expose your local server
ngrok http 8000

# Use the HTTPS URL for webhook
# Example: https://abc123.ngrok.io/api/v1/whatsapp/webhook
```

#### Option B: Deploy to Cloud

- Deploy to Heroku, Railway, DigitalOcean, etc.
- Use your production URL for webhook

### Step 7: Configure Webhook in Meta Dashboard

1. Go to WhatsApp → Configuration
2. Add webhook URL: `https://yourdomain.com/api/v1/whatsapp/webhook`
3. Add verify token: Your chosen verify token
4. Subscribe to: `messages` and `message_status`

## 💰 Pricing Breakdown

### Free Tier (Perfect for Development)

- ✅ **1,000 conversations/month** - FREE
- ✅ Test with up to 5 phone numbers
- ✅ All WhatsApp features available

### Production Pricing (Pay-as-you-go)

- 📱 **User-initiated conversations**: $0.005-$0.015 per conversation
- 🤖 **Business-initiated conversations**: $0.025-$0.09 per conversation
- 💬 **24-hour conversation window** (multiple messages count as 1 conversation)

### Example Monthly Costs

- **100 conversations/month**: ~$2-5
- **1,000 conversations/month**: ~$10-30
- **10,000 conversations/month**: ~$50-200

## 🔧 Testing Your Setup

Once configured, test with these commands:

```bash
# 1. Check webhook status
curl http://localhost:8000/api/v1/whatsapp/webhook/status

# 2. Test webhook verification
curl "http://localhost:8000/api/v1/whatsapp/webhook?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=YOUR_VERIFY_TOKEN"

# 3. Test message processing
curl -X POST "http://localhost:8000/api/v1/whatsapp/webhook" \
  -H "Content-Type: application/json" \
  -d '{"entry":[{"changes":[{"value":{"messages":[{"id":"test","from":"1234567890","text":{"body":"Hello test"}}]}}]}]}'
```

## 🚨 Important Security Notes

1. **Never commit credentials to git**
2. **Use environment variables for all secrets**
3. **Validate webhook signatures in production**
4. **Use HTTPS for all webhook URLs**

## 📞 Support

- Meta Developer Docs: https://developers.facebook.com/docs/whatsapp
- WhatsApp Business API Docs: https://developers.facebook.com/docs/whatsapp/cloud-api
- This project's webhook endpoints: http://localhost:8000/docs
