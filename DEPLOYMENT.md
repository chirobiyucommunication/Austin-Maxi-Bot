# Austin Maxi Bot - Deployment Guide

## Local Deployment

### Step 1: Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium
```

### Step 2: Configure

```bash
# Edit config.py with your credentials
nano config.py
```

Required settings:
- `ADMIN_BOT_TOKEN` - From @BotFather
- `CLIENT_BOT_TOKEN` - From @BotFather
- `ADMIN_CHAT_ID` - Your Telegram chat ID
- `USER_CHAT_ID` - User receiving signals
- `POCKET_OPTION_EMAIL` - Your PO account
- `POCKET_OPTION_PASSWORD` - Your PO password

### Step 3: Run Locally

**Start all services in separate terminals:**

```bash
# Terminal 1: License Server (Port 5000)
python server.py

# Terminal 2: Signal Server (Port 5001)
python signal_bot.py

# Terminal 3: Admin Bot
python admin_bot.py

# Terminal 4: Client Bot
python client_bot.py
```

### Step 4: Test

Send commands to your Telegram bots:

**Admin Bot:**
```
/start
/devices
/signal_test
```

**Client Bot:**
```
/start
/device
/status
```

---

## Production Deployment (Render)

### Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up and create account
3. Connect GitHub (optional, but recommended)

### Deploy License Server

1. Click "New +" → "Web Service"
2. Fill in:
   - Name: `austin-maxi-license-server`
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn server:app`
   - Environment: Python 3.9
   - Instance: Free tier OK

3. Add environment variables:
   - `ADMIN_SECRET`: Your secure password

4. Click "Create Web Service"

5. Copy the service URL (e.g., `https://austin-maxi-license-server.onrender.com`)

### Deploy Signal Server

1. Repeat steps for Signal Server:
   - Name: `austin-maxi-signal-server`
   - Start command: `gunicorn signal_bot:app`

2. Copy the service URL

### Update Configuration

Update `config.py` with Render URLs:

```python
LICENSE_SERVER_URL = "https://austin-maxi-license-server.onrender.com"
SIGNAL_SERVER_URL = "https://austin-maxi-signal-server.onrender.com"
```

### Deploy Bots (Local or Server)

The Telegram bots can run locally or on any Python server:

**Option A: Keep running locally**
```bash
python admin_bot.py &
python client_bot.py &
```

**Option B: Deploy to Render as Background Workers**

→ *Note: Render doesn't support long-running bots. Use local or alternatives like AWS Lambda.*

---

## TradingView Integration

### Send signals from TradingView alerts:

1. In TradingView, create an alert
2. Webhook URL: `https://austin-maxi-signal-server.onrender.com/signal`
3. Message format (JSON):

```json
{
  "pair": "{{ticker}}",
  "direction": "BUY",
  "timeframe": "{{interval}}",
  "strength": "STRONG",
  "entry_price": {{close}},
  "stop_loss": {{open}},
  "take_profit": {{high}},
  "source": "TradingView"
}
```

---

## Docker Deployment (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "server.py"]
```

Build and run:

```bash
docker build -t austin-maxi-bot .
docker run -p 5000:5000 austin-maxi-bot
```

---

## Monitoring

### Check Render Logs

1. Go to Render dashboard
2. Click on service
3. View "Logs" tab

### Monitor Locally

Check files:
- `data/licenses.json` - Device status
- `data/signals.json` - Signal history
- `data/trade_log.json` - Trade records

### Health Check Endpoints

```bash
# License Server
curl https://austin-maxi-license-server.onrender.com/

# Signal Server
curl https://austin-maxi-signal-server.onrender.com/
```

---

## Scaling

### Multiple Clients

The License Server supports unlimited devices:

1. Generate Device ID on each client: `python client_bot.py`
2. Activate in Admin Bot: `/activate <device_id>`
3. Each client runs independently

### Database (Future)

For production, replace JSON files with PostgreSQL:

```python
# Use SQLAlchemy for ORM
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://user:password@host/dbname"
engine = create_engine(DATABASE_URL)
```

---

## Security Checklist

- [ ] Change `ADMIN_SECRET` in config
- [ ] Use strong Telegram bot tokens
- [ ] Enable HTTPS (Render does this automatically)
- [ ] Rotate Pocket Option password periodically
- [ ] Monitor license activations
- [ ] Review trade logs regularly
- [ ] Keep dependencies updated: `pip install -r requirements.txt --upgrade`
- [ ] Use environment variables for sensitive data

---

## Troubleshooting

### Render Service stops

Check logs:
```
Service crashed: Memory/CPU exceeded
→ Upgrade to paid instance
```

### API timeout

Increase timeout in requests:
```python
requests.get(url, timeout=30)
```

### Telegram rate limits

Add delay between messages:
```python
import time
time.sleep(1)  # 1 second between messages
```

---

## Support & Updates

- Monitor [Render status](https://status.render.com/)
- Check Python version compatibility
- Update dependencies monthly
- Test in staging before production

---

**Deployment Date:** February 14, 2026
