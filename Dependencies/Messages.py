import threading
from queue import Queue
from twilio.rest import Client
import logging
import time

# --- Twilio WhatsApp Setup ---
SID = 'ACab496632855d21ce58d0fbddea1de18e'
TOKEN = '0dd400a032e35cb2fa5859c8f5c20d84'
FROM_NUMBER = 'whatsapp:+14155238886'
TO_NUMBER = 'whatsapp:+917619109684'

# --- Shared Queue and Worker Flag ---
message_queue = Queue()
worker_started = False  # ✅ Prevent multiple worker threads


def whatsapp_worker():
    logging.info("✅ WhatsApp message worker started in background thread.")
    client = Client(SID, TOKEN)
    while True:
        msg = message_queue.get()
        if msg is None:
            break
        try:
            client.messages.create(
                from_=FROM_NUMBER,
                to=TO_NUMBER,
                body=msg
            )
            logging.info(f"📤 WhatsApp sent: {msg}")
        except Exception as e:
            logging.error(f"❌ WhatsApp send error: {e}")
        finally:
            message_queue.task_done()
        time.sleep(1)  # Small delay for Twilio rate limits


def start_whatsapp_worker():
    """Start background worker once only"""
    global worker_started
    if not worker_started:
        t = threading.Thread(target=whatsapp_worker, daemon=True)
        t.start()
        worker_started = True
    else:
        logging.debug("⚙️ WhatsApp worker already running — skipped restart.")


def queue_whatsapp_message(message):
    """Put message into queue"""
    message_queue.put(message)


# --- Example usage (only when run directly) ---
# if __name__ == "__main__":
#     start_whatsapp_worker()
#     queue_whatsapp_message("🚀 WhatsApp message sender started...")
#     time.sleep(5)
#     stop_whatsapp_worker()
