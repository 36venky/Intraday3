from queue import Queue
from threading import Thread
import logging , os

# Global write queue
write_queue = Queue()

def writer_worker():
    
    while True:
        try:
            filepath, text = write_queue.get()

            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(text)
        except Exception as e:
            logging.error(f"Writer error for {filepath}: {e}")
        finally:
            write_queue.task_done()


# Start the writer thread ONCE
Thread(target=writer_worker, daemon=True).start()


def write(filename, text):

    base_dir = os.path.dirname(os.path.abspath(__file__))   # folder of Dependencies/
    main_dir = os.path.dirname(base_dir)                    # parent (your project folder)
    filepath = os.path.join(main_dir, filename)
    try:
        write_queue.put((filepath, text))
    except Exception as e:
        logging.error(f"Queue put failed for {filepath}: {e}")
