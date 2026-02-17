import tkinter as tk
from tkinter import filedialog, Canvas
import threading
import os

# connect backend
from rag_backend import ask_pdf, load_pdf


# ============================================
# MODERN BUTTON CLASS WITH HOVER EFFECTS
# ============================================
class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command, bg_color, hover_color, text_color="#FFFFFF", **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.text = text
        
        self.configure(bg=bg_color, cursor="hand2")
        
        # Create rounded rectangle button
        self.create_rounded_rect(0, 0, kwargs.get('width', 120), kwargs.get('height', 45), 
                                 radius=22, fill=bg_color, outline="")
        
        # Add text
        self.create_text(kwargs.get('width', 120)//2, kwargs.get('height', 45)//2, 
                        text=text, fill=text_color, 
                        font=("new times roman", 12, "bold"))
        
        # Bind events
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1+radius, y1,
                  x1+radius, y1,
                  x2-radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1+radius,
                  x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def on_enter(self, e):
        self.configure(bg=self.hover_color)
        self.delete("all")
        self.create_rounded_rect(0, 0, self.winfo_width(), self.winfo_height(), 
                                radius=22, fill=self.hover_color, outline="")
        self.create_text(self.winfo_width()//2, self.winfo_height()//2, 
                        text=self.text, fill=self.text_color, 
                        font=("new times roman", 12, "bold"))
    
    def on_leave(self, e):
        self.configure(bg=self.bg_color)
        self.delete("all")
        self.create_rounded_rect(0, 0, self.winfo_width(), self.winfo_height(), 
                                radius=22, fill=self.bg_color, outline="")
        self.create_text(self.winfo_width()//2, self.winfo_height()//2, 
                        text=self.text, fill=self.text_color, 
                        font=("new times roman", 12, "bold"))
    
    def on_click(self, e):
        if self.command:
            self.command()


# ============================================
# GRADIENT BACKGROUND CLASS
# ============================================
class GradientFrame(tk.Canvas):
    def __init__(self, parent, color1, color2, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.color1 = color1
        self.color2 = color2
        self.bind("<Configure>", self._draw_gradient)
        
    def _draw_gradient(self, event=None):
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        limit = height
        
        # Parse colors
        r1, g1, b1 = self.winfo_rgb(self.color1)
        r2, g2, b2 = self.winfo_rgb(self.color2)
        
        r_ratio = (r2 - r1) / limit
        g_ratio = (g2 - g1) / limit
        b_ratio = (b2 - b1) / limit
        
        for i in range(limit):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = f'#{nr>>8:02x}{ng>>8:02x}{nb>>8:02x}'
            self.create_line(0, i, width, i, tags=("gradient",), fill=color)
        self.lower("gradient")


# ============================================
# MAIN WINDOW SETUP
# ============================================
root = tk.Tk()
root.title("✨ AI PDF Assistant - Next Gen")
root.geometry("1000x750")
root.configure(bg="#E8F4F8")

# Set minimum size
root.minsize(900, 650)
root.resizable(False, False)  



# ============================================
# HEADER WITH GRADIENT
# ============================================
header = GradientFrame(root, "#A8E6CF", "#DCEEF7", height=80, highlightthickness=0)
header.pack(fill="x")

# Title with modern styling
title_frame = tk.Frame(header, bg="#A8E6CF")
title_frame.place(relx=0.5, rely=0.5, anchor="center")

title = tk.Label(title_frame, text="✨ AI PDF Assistant",
                 font=("new times roman", 26, "bold"),
                 bg="#A8E6CF", fg="#1A5F7A")
title.pack()

subtitle = tk.Label(title_frame, text="Next Generation Document Intelligence",
                   font=("new times roman", 11),
                   bg="#A8E6CF", fg="#2C7A9B")
subtitle.pack()


# ============================================
# UPLOAD BUTTON IN HEADER
# ============================================
def upload_pdf():
    paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
    if not paths:
        return

    def worker():
        for path in paths:
            name = os.path.basename(path)
            root.after(0, lambda n=name: add_message(f"📄 Loading {n}...", "bot"))
            try:
                load_pdf(path)
                root.after(0, lambda n=name: add_message(f"✅ {n} is ready!", "bot"))
            except Exception as e:
                root.after(0, lambda err=str(e): add_message(f"❌ Error: {err}", "bot"))

    threading.Thread(target=worker, daemon=True).start()


upload_btn = ModernButton(header, "📤 Upload PDF", upload_pdf, 
                          bg_color="#16A34A", hover_color="#B1ECBE",
                          width=160, height=50)
upload_btn.place(relx=0.85, rely=0.5, anchor="center")


# ============================================
# CHAT AREA WITH GRADIENT BACKGROUND
# ============================================
chat_container = GradientFrame(root, "#F0F8FF", "#E8F4F8", highlightthickness=0)
chat_container.pack(fill="both", expand=True, padx=20, pady=20)

chat_canvas = tk.Canvas(chat_container, bg="#F0F8FF", highlightthickness=0)
scrollbar = tk.Scrollbar(chat_container, command=chat_canvas.yview, 
                        bg="#B8E6F0", troughcolor="#E8F4F8", 
                        activebackground="#7DD3E8", width=12)
chat_frame = tk.Frame(chat_canvas, bg="#FFFFFF")

chat_frame.bind(
    "<Configure>",
    lambda e: chat_canvas.configure(scrollregion=chat_canvas.bbox("all"))
)

chat_canvas.create_window((0, 0), window=chat_frame, anchor="nw")
chat_canvas.configure(yscrollcommand=scrollbar.set)

chat_canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")


# ============================================
# MESSAGE BUBBLES WITH MODERN DESIGN
# ============================================
def add_message(text, sender="bot"):
    wrapper = tk.Frame(chat_frame, bg="#F0F8FF")

    if sender == "user":
        # User message bubble - right side with blue gradient
        bubble_frame = tk.Frame(wrapper, bg="#F0F8FF")
        
        bubble = tk.Label(bubble_frame,
                         text=text,
                         bg="#B0F9FE",
                         fg="#003D5C",
                         wraplength=550,
                         justify="left",
                         font=("new times roman", 11),
                         padx=18, pady=12,
                         relief="flat",
                         borderwidth=0)
        bubble.pack(anchor="e", pady=8)
        bubble_frame.pack(anchor="e")
        
    else:
        # Bot message bubble - left side with green gradient
        bubble_frame = tk.Frame(wrapper, bg="#F0F8FF")
        
        # Add AI icon
        icon_label = tk.Label(bubble_frame, text="🤖", 
                            font=("new times roman", 16),
                            bg="#F0F8FF")
        icon_label.pack(side="left", padx=(15, 5))
        
        bubble = tk.Label(bubble_frame,
                         text=text,
                         bg="#C8F7DC",
                         fg="#004D29",
                         wraplength=550,
                         justify="left",
                         font=("new times roman", 11),
                         padx=18, pady=12,
                         relief="flat",
                         borderwidth=0)
        bubble.pack(side="left", anchor="w", pady=8)
        bubble_frame.pack(anchor="w")

    wrapper.pack(fill="both", expand=True, pady=5)
    root.update_idletasks()
    chat_canvas.yview_moveto(1.0)


# Welcome message
add_message("👋 Hello! Welcome to the AI PDF Assistant.\n\n✨ Upload your PDF documents and ask me anything about them.\nI'm powered by advanced AI to help you understand your documents better!", "bot")


# ============================================
# INPUT AREA WITH MODERN DESIGN
# ============================================
input_container = tk.Frame(root, bg="#FFFFFF", height=100)
input_container.pack(fill="x", padx=20, pady=(0, 20))

# Add shadow effect
shadow = tk.Frame(root, bg="#D0E8F0", height=2)
shadow.place(in_=input_container, relx=0, rely=0, relwidth=1)

input_frame = tk.Frame(input_container, bg="#FFFFFF")
input_frame.pack(fill="both", expand=True, padx=15, pady=15)

# Input text area with modern styling
user_input = tk.Text(input_frame,
                     height=1,
                     font=("new times roman", 12),
                     wrap="word",
                     bg="#F8FCFF",
                     fg="#1A5F7A",
                     relief="flat",
                     borderwidth=2,
                     highlightthickness=1,
                     highlightbackground="#B8E6F0",
                     highlightcolor="#7DD3E8",
                     insertbackground="#1A5F7A",
                     padx=10, pady=10)
user_input.pack(side="left", fill="both", expand=True, padx=(10, 5))

# Placeholder text
placeholder = "💬 Type your question here..."
user_input.insert("1.0", placeholder)
user_input.config(fg="#A0C4D0")

def on_focus_in(event):
    if user_input.get("1.0", "end-1c") == placeholder:
        user_input.delete("1.0", tk.END)
        user_input.config(fg="#1A5F7A")

def on_focus_out(event):
    if not user_input.get("1.0", "end-1c"):
        user_input.insert("1.0", placeholder)
        user_input.config(fg="#A0C4D0")

user_input.bind("<FocusIn>", on_focus_in)
user_input.bind("<FocusOut>", on_focus_out)


# ============================================
# SEND MESSAGE FUNCTION
# ============================================
def send_message():
    text = user_input.get("1.0", tk.END).strip()
    if not text or text == placeholder:
        return

    user_input.delete("1.0", tk.END)
    add_message(text, "user")
    add_message("💭 Analyzing your question...", "bot")

    def worker():
        try:
            reply = ask_pdf(text)
        except Exception as e:
            reply = f"❌ Error: {e}"

        root.after(0, lambda: add_message(reply, "bot"))

    threading.Thread(target=worker, daemon=True).start()


# Send button with modern design
send_btn = ModernButton(input_frame, "🚀 Send", send_message,
                       bg_color="#5BC0DE", hover_color="#7DD3E8",
                       width=120, height=50)
send_btn.pack(side="right")


# ============================================
# KEYBOARD SHORTCUTS
# ============================================
def enter_send(event):
    send_message()
    return "break"

user_input.bind("<Return>", enter_send)
user_input.bind("<Shift-Return>", lambda e: None)  # Allow Shift+Enter for new line


# ============================================
# SAFE CLOSING
# ============================================
def on_close():
    root.destroy()
    os._exit(0)

root.protocol("WM_DELETE_WINDOW", on_close)


# ============================================
# START APPLICATION
# ============================================
root.mainloop()