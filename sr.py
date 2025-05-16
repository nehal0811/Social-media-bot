import os
import time
import pandas as pd
import nltk
import threading
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox
from nltk.tokenize import word_tokenize
from PIL import Image

# Download required data once
nltk.download('punkt')
nltk.download('stopwords')

# ----- Perspective API content check (Placeholder) -----
def check_content_appropriateness(text):
    print("⚠️ Skipping content check (API temporarily disabled)")
    return True  # Simulate always appropriate

# ----- Determine best time slot -----
def get_best_post_time():
    now = datetime.now()
    today = now.date()
    slots = [datetime(today.year, today.month, today.day, h) for h in [9, 12, 18]]
    future = [s for s in slots if s > now]
    return future[0] if future else slots[0] + timedelta(days=1)

# ----- Extract important keywords -----
def extract_key_points(text):
    keywords = ["innovation", "AI", "efficiency", "automation", "customer", "growth", "technology"]
    return list(set([kw for kw in keywords if kw.lower() in text.lower()]))

# ----- Generate suggested captions from image name -----
def suggest_captions_from_filename(filename):
    name = os.path.basename(filename).split('.')[0].replace('_', ' ').replace('-', ' ')
    suggestions = [
        f"Discover how {name} can inspire innovation.",
        f"The future is now: Embrace {name}.",
        f"Here’s how {name} drives growth.",
        f"Empowering change through {name}.",
        f"Let’s talk about {name} and technology."
    ]
    return suggestions

# ----- Display preview -----
def display_ui_preview(caption, platform, file_path, scheduled_time, reminder_time):
    print("\n📢 POST SCHEDULER PREVIEW")
    print("══════════════════════════════════════")
    print(f"🟢 Platform     : {platform.upper()}")
    print(f"📅 Scheduled    : {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ Reminder Set : {reminder_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📝 Caption      : {caption}")

    if platform.lower() == 'youtube' or file_path.lower().endswith('.mp4'):
        print("🎞️ Video Preview: Opening video externally...")
        os.startfile(file_path)
    else:
        print("🖼️ Image Preview: Opening image...")
        try:
            Image.open(file_path).show()
        except Exception as e:
            print(f"❌ Cannot preview image: {e}")
    print("══════════════════════════════════════\n")

# ----- Log post -----
def log_post(caption, platform, file_path):
    log_file = 'post_history.xlsx'
    try:
        df = pd.read_excel(log_file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Timestamp", "Platform", "Caption", "File"])
    new_entry = {
        "Timestamp": datetime.now(),
        "Platform": platform,
        "Caption": caption,
        "File": os.path.basename(file_path)
    }
    df = pd.concat([df, pd.DataFrame([new_entry])])
    df.to_excel(log_file, index=False)
    print("📁 Post logged to post_history.xlsx")

# ----- Schedule Post Logic -----
def schedule_post(caption, file_path, platform='facebook'):
    print("📝 Checking content appropriateness...")
    if not check_content_appropriateness(caption):
        print("❌ Inappropriate content flagged.")
        return

    highlights = extract_key_points(caption)
    if highlights:
        print(f"🌟 Highlights Detected: {', '.join(highlights)}")

    scheduled_time = get_best_post_time()
    reminder_time = scheduled_time - timedelta(minutes=15)

    display_ui_preview(caption, platform, file_path, scheduled_time, reminder_time)

    messagebox.showinfo("Scheduled", f"Post will be published at {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}\nReminder set for {reminder_time.strftime('%Y-%m-%d %H:%M:%S')}")

    delay = (scheduled_time - datetime.now()).total_seconds()
    if delay > 0:
        print(f"🕒 Waiting {int(delay)} seconds until posting...")
        time.sleep(delay)

    post_time = datetime.now()
    print(f"🚀 Posting to {platform.upper()} at {post_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 File Used: {file_path}")
    log_post(caption, platform, file_path)

# ----- GUI Logic -----
def browse_file():
    path = filedialog.askopenfilename(filetypes=[("Media files", "*.png *.jpg *.jpeg *.mp4")])
    media_entry.delete(0, tk.END)
    media_entry.insert(0, path)
    suggested_captions = suggest_captions_from_filename(path)
    caption_suggestion_box['values'] = suggested_captions
    if suggested_captions:
        caption_suggestion_box.current(0)

def use_suggested_caption():
    caption_text.delete("1.0", tk.END)
    caption_text.insert(tk.END, caption_suggestion_box.get())

def start_posting():
    caption = caption_text.get("1.0", tk.END).strip()
    media = media_entry.get()
    platform = platform_combo.get()

    if not caption or not media or not platform:
        messagebox.showerror("Missing Fields", "All fields are required!")
        return

    threading.Thread(target=schedule_post, args=(caption, media, platform)).start()

def run_gui():
    global caption_text, media_entry, platform_combo, caption_suggestion_box

    root = tk.Tk()
    root.title("📣 Smart Social Media Scheduler")
    root.geometry("540x500")

    tk.Label(root, text="📝 Caption:", font=('Arial', 12)).pack(pady=(10, 0))
    caption_text = tk.Text(root, height=5, width=60)
    caption_text.pack(pady=5)

    tk.Label(root, text="💡 Suggested Captions:", font=('Arial', 12)).pack(pady=(10, 0))
    caption_suggestion_box = Combobox(root, width=60)
    caption_suggestion_box.pack(pady=5)
    tk.Button(root, text="Use Suggested Caption", command=use_suggested_caption).pack()

    tk.Label(root, text="📁 Image/Video Path:", font=('Arial', 12)).pack()
    media_entry = tk.Entry(root, width=50)
    media_entry.pack(pady=5)
    tk.Button(root, text="Browse File", command=browse_file).pack()

    tk.Label(root, text="🌐 Platform:", font=('Arial', 12)).pack(pady=(10, 0))
    platform_combo = Combobox(root, values=["facebook", "instagram", "linkedin", "youtube", "twitter"])
    platform_combo.set("facebook")
    platform_combo.pack()

    tk.Button(root, text="📤 Schedule Post", command=start_posting, bg="#4CAF50", fg="white", padx=10, pady=5).pack(pady=20)

    root.mainloop()

# ----- Entry Point -----
if __name__ == "__main__":
    run_gui()
