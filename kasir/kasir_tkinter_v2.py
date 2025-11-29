import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import json
import os
from PIL import Image, ImageTk

class KedaiHaunaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kedai Hauna - Aplikasi Kasir")
        self.root.geometry("1400x800")
        self.root.configure(bg="#0a0a0a")
        
        # Colors (sama dengan web)
        self.colors = {
            'bg_dark': '#0a0a0a',
            'bg_card': '#1a1a1a',
            'bg_sidebar': '#000000',
            'text_white': '#ffffff',
            'text_gray': '#999999',
            'accent': '#ff4444',
            'border': '#333333'
        }
        
        # Data menu
        self.menu_items = [
            {"id": 1, "name": "Bakso Malang", "price": 23000, "image": "static/images/Bakso malang.jpg"},
            {"id": 2, "name": "Seblak Special", "price": 16000, "image": "static/images/Seblak special.jpg"},
            {"id": 3, "name": "Mie Ayam", "price": 18000, "image": "static/images/Mie Ayam.jpg"},
            {"id": 4, "name": "Siomay", "price": 11000, "image": "static/images/Siomay.jpg"},
            {"id": 5, "name": "Tea", "price": 6000, "image": "static/images/Tea.jpg", "has_variant": True, "variants": ["Dingin", "Hangat"]},
            {"id": 6, "name": "Ayam Crispy", "price": 17000, "image": "static/images/Ayam Crispy.jpg"},
            {"id": 7, "name": "Nasi", "price": 5000, "image": "static/images/Nasi.jpg"},
        ]
        
        self.cart = []
        self.transactions = self.load_transactions()
        self.images = {}
        
        self.load_images()
        self.setup_ui()
        self.update_cart_display()  # Initialize cart display
        
        # Notification queue and history
        self.notification_queue = []
        self.notification_history = []
    
    def show_notification(self, message, duration=3000, type="success"):
        """Tampilkan notifikasi toast di pojok kanan atas"""
        # Save to history
        self.notification_history.insert(0, {
            'message': message,
            'type': type,
            'time': datetime.now().strftime('%H:%M:%S')
        })
        
        # Keep only last 50 notifications
        if len(self.notification_history) > 50:
            self.notification_history = self.notification_history[:50]
        
        # Create notification window
        notif = tk.Toplevel(self.root)
        notif.overrideredirect(True)  # Remove window decorations
        notif.attributes('-topmost', True)  # Always on top
        
        # Set background color based on type
        bg_color = "#4CAF50" if type == "success" else "#ff4444" if type == "error" else "#2196F3"
        
        # Create frame
        frame = tk.Frame(notif, bg=bg_color, padx=20, pady=15)
        frame.pack()
        
        # Icon based on type
        icon = "✓" if type == "success" else "✗" if type == "error" else "ℹ"
        
        # Icon label
        tk.Label(frame, text=icon, font=("Arial", 16, "bold"), 
                bg=bg_color, fg="white").pack(side=tk.LEFT, padx=(0, 10))
        
        # Message label
        tk.Label(frame, text=message, font=("Segoe UI", 11), 
                bg=bg_color, fg="white", wraplength=300).pack(side=tk.LEFT)
        
        # Position at top right
        notif.update_idletasks()
        width = notif.winfo_width()
        height = notif.winfo_height()
        
        # Calculate position (top right with offset)
        x = self.root.winfo_x() + self.root.winfo_width() - width - 20
        y = self.root.winfo_y() + 20 + (len(self.notification_queue) * (height + 10))
        
        notif.geometry(f"+{x}+{y}")
        
        # Add to queue
        self.notification_queue.append(notif)
        
        # Fade in animation
        notif.attributes('-alpha', 0.0)
        self.fade_in(notif, 0.0)
        
        # Auto close after duration
        def close_notification():
            self.fade_out(notif, 1.0)
            if notif in self.notification_queue:
                self.notification_queue.remove(notif)
            # Reposition remaining notifications
            self.reposition_notifications()
        
        notif.after(duration, close_notification)
    
    def fade_in(self, window, alpha):
        """Fade in animation"""
        if alpha < 1.0:
            alpha += 0.1
            window.attributes('-alpha', alpha)
            window.after(30, lambda: self.fade_in(window, alpha))
    
    def fade_out(self, window, alpha):
        """Fade out animation"""
        if alpha > 0.0:
            alpha -= 0.1
            window.attributes('-alpha', alpha)
            window.after(30, lambda: self.fade_out(window, alpha))
        else:
            window.destroy()
    
    def reposition_notifications(self):
        """Reposition notifications after one is closed"""
        for idx, notif in enumerate(self.notification_queue):
            notif.update_idletasks()
            width = notif.winfo_width()
            height = notif.winfo_height()
            x = self.root.winfo_x() + self.root.winfo_width() - width - 20
            y = self.root.winfo_y() + 20 + (idx * (height + 10))
            notif.geometry(f"+{x}+{y}")
    
    def show_notification_history(self):
        """Tampilkan history notifikasi"""
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Riwayat Notifikasi")
        dialog.geometry("500x600")
        dialog.configure(bg=self.colors['bg_card'])
        dialog.transient(self.root)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Header
        header = tk.Frame(dialog, bg=self.colors['bg_card'])
        header.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(header, text="🔔 Riwayat Notifikasi", font=("Segoe UI", 14, "bold"),
                bg=self.colors['bg_card'], fg="white").pack(side=tk.LEFT)
        
        tk.Button(header, text="×", font=("Arial", 18), bg=self.colors['bg_card'],
                 fg="white", relief=tk.FLAT, command=dialog.destroy).pack(side=tk.RIGHT)
        
        # Clear all button
        if self.notification_history:
            tk.Button(header, text="Hapus Semua", font=("Segoe UI", 10), 
                     bg=self.colors['accent'], fg="white", relief=tk.FLAT,
                     command=lambda: self.clear_notification_history(dialog),
                     padx=10, pady=5).pack(side=tk.RIGHT, padx=10)
        
        # Scrollable list
        canvas = tk.Canvas(dialog, bg=self.colors['bg_card'], highlightthickness=0)
        scrollbar = tk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        list_frame = tk.Frame(canvas, bg=self.colors['bg_card'])
        
        list_frame.bind("<Configure>", 
                       lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Display notifications
        if not self.notification_history:
            tk.Label(list_frame, text="Belum ada notifikasi", font=("Segoe UI", 11),
                    bg=self.colors['bg_card'], fg=self.colors['text_gray']).pack(pady=50)
        else:
            for notif in self.notification_history:
                self.create_notification_item(list_frame, notif)
    
    def create_notification_item(self, parent, notif):
        """Create notification item in history"""
        item_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        item_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Icon based on type
        icon = "✓" if notif['type'] == "success" else "✗" if notif['type'] == "error" else "ℹ"
        icon_color = "#4CAF50" if notif['type'] == "success" else "#ff4444" if notif['type'] == "error" else "#2196F3"
        
        # Left: Icon
        tk.Label(item_frame, text=icon, font=("Arial", 14, "bold"),
                bg=self.colors['bg_dark'], fg=icon_color, width=3).pack(side=tk.LEFT, padx=10, pady=10)
        
        # Middle: Message
        msg_frame = tk.Frame(item_frame, bg=self.colors['bg_dark'])
        msg_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(msg_frame, text=notif['message'], font=("Segoe UI", 10),
                bg=self.colors['bg_dark'], fg="white", anchor="w", wraplength=350).pack(fill=tk.X)
        tk.Label(msg_frame, text=notif['time'], font=("Segoe UI", 9),
                bg=self.colors['bg_dark'], fg=self.colors['text_gray'], anchor="w").pack(fill=tk.X)
    
    def clear_notification_history(self, dialog):
        """Clear all notification history"""
        if messagebox.askyesno("Konfirmasi", "Hapus semua riwayat notifikasi?"):
            self.notification_history = []
            dialog.destroy()
            self.show_notification("Riwayat notifikasi dihapus", duration=2000, type="info")
    
    def load_images(self):
        """Load dan resize gambar menu"""
        for item in self.menu_items:
            try:
                if os.path.exists(item['image']):
                    img = Image.open(item['image'])
                    # Resize untuk card yang lebih kecil
                    img = img.resize((200, 150), Image.Resampling.LANCZOS)
                    self.images[item['id']] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Error loading {item['image']}: {e}")
    
    def setup_ui(self):
        # Container utama
        main_container = tk.Frame(self.root, bg=self.colors['bg_dark'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar kiri
        self.setup_sidebar(main_container)
        
        # Content area tengah
        self.content_frame = tk.Frame(main_container, bg=self.colors['bg_dark'])
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Sidebar kanan (cart)
        self.setup_cart_sidebar(main_container)
        
        # Show kasir page
        self.show_kasir_page()

    def setup_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=self.colors['bg_sidebar'], width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Logo
        logo_frame = tk.Frame(sidebar, bg=self.colors['bg_sidebar'])
        logo_frame.pack(pady=25, padx=15)
        
        # Logo icon dengan background merah rounded
        logo_bg = tk.Frame(logo_frame, bg=self.colors['accent'], width=50, height=50)
        logo_bg.pack()
        logo_bg.pack_propagate(False)
        
        logo_icon = tk.Label(logo_bg, text="🍜", font=("Arial", 24), 
                            bg=self.colors['accent'], fg="white")
        logo_icon.pack(expand=True)
        
        logo_text = tk.Label(logo_frame, text="Kedai\nHauna", font=("Segoe UI", 13, "bold"), 
                            bg=self.colors['bg_sidebar'], fg="white", justify=tk.LEFT)
        logo_text.pack(pady=8)
        
        # Menu buttons
        menu_frame = tk.Frame(sidebar, bg=self.colors['bg_sidebar'])
        menu_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        self.btn_kasir = tk.Button(menu_frame, text="💰 Kasir", font=("Segoe UI", 11), 
                                   bg="white", fg=self.colors['accent'], relief=tk.FLAT,
                                   command=self.show_kasir_page, anchor="w", padx=18, pady=13,
                                   cursor="hand2", borderwidth=0)
        self.btn_kasir.pack(fill=tk.X, pady=4)
        
        self.btn_pemasukan = tk.Button(menu_frame, text="📊 Pemasukan", font=("Segoe UI", 11),
                                       bg=self.colors['bg_card'], fg=self.colors['text_gray'], 
                                       relief=tk.FLAT, command=self.show_pemasukan_page, 
                                       anchor="w", padx=18, pady=13, cursor="hand2", borderwidth=0)
        self.btn_pemasukan.pack(fill=tk.X, pady=4)
        
        # Logout button
        tk.Button(sidebar, text="🚪 Logout", font=("Segoe UI", 11), 
                 bg=self.colors['bg_card'], fg=self.colors['text_gray'], relief=tk.FLAT,
                 command=self.root.quit, anchor="w", padx=18, pady=13, cursor="hand2",
                 borderwidth=0).pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=20)

    def setup_cart_sidebar(self, parent):
        cart_sidebar = tk.Frame(parent, bg=self.colors['bg_sidebar'], width=300)
        cart_sidebar.pack(side=tk.RIGHT, fill=tk.Y)
        cart_sidebar.pack_propagate(False)
        
        # Profile card
        profile_frame = tk.Frame(cart_sidebar, bg=self.colors['bg_card'])
        profile_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(profile_frame, text="👩", font=("Arial", 40), 
                bg="#333333", fg="white").pack(pady=15)
        tk.Label(profile_frame, text="Hauna Balqis", font=("Arial", 13, "bold"),
                bg=self.colors['bg_card'], fg="white").pack()
        tk.Label(profile_frame, text="📍 Purbalingga, Indonesia", font=("Arial", 9),
                bg=self.colors['bg_card'], fg=self.colors['text_gray']).pack(pady=8)
        
        # Cart section
        cart_section = tk.Frame(cart_sidebar, bg=self.colors['bg_card'])
        cart_section.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Cart header
        cart_header = tk.Frame(cart_section, bg=self.colors['bg_card'])
        cart_header.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(cart_header, text="Keranjang Belanja", font=("Arial", 12, "bold"),
                bg=self.colors['bg_card'], fg="white").pack(side=tk.LEFT)
        tk.Button(cart_header, text="🗑️", font=("Arial", 12), bg=self.colors['bg_card'],
                 fg="white", relief=tk.FLAT, command=self.clear_cart).pack(side=tk.RIGHT)
        
        # Cart items scrollable dengan height yang fixed
        cart_scroll_container = tk.Frame(cart_section, bg=self.colors['bg_card'], height=280)
        cart_scroll_container.pack(fill=tk.X, padx=15)
        cart_scroll_container.pack_propagate(False)
        
        canvas = tk.Canvas(cart_scroll_container, bg=self.colors['bg_card'], highlightthickness=0)
        scrollbar = tk.Scrollbar(cart_scroll_container, orient="vertical", command=canvas.yview)
        self.cart_items_frame = tk.Frame(canvas, bg=self.colors['bg_card'])
        
        self.cart_items_frame.bind("<Configure>", 
                                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.cart_items_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Summary
        summary_frame = tk.Frame(cart_section, bg=self.colors['bg_card'])
        summary_frame.pack(fill=tk.X, padx=15, pady=15)
        
        self.subtotal_label = tk.Label(summary_frame, text="Subtotal: Rp 0", 
                                       font=("Arial", 10), bg=self.colors['bg_card'], 
                                       fg="white", anchor="w")
        self.subtotal_label.pack(fill=tk.X, pady=3)
        
        self.tax_label = tk.Label(summary_frame, text="Pajak (10%): Rp 0",
                                  font=("Arial", 10), bg=self.colors['bg_card'],
                                  fg="white", anchor="w")
        self.tax_label.pack(fill=tk.X, pady=3)
        
        tk.Frame(summary_frame, bg=self.colors['border'], height=2).pack(fill=tk.X, pady=8)
        
        self.total_label = tk.Label(summary_frame, text="Total: Rp 0",
                                    font=("Arial", 14, "bold"), bg=self.colors['bg_card'],
                                    fg="white", anchor="w")
        self.total_label.pack(fill=tk.X, pady=5)
        
        tk.Button(summary_frame, text="Bayar Sekarang", font=("Arial", 12, "bold"),
                 bg=self.colors['accent'], fg="white", relief=tk.FLAT,
                 command=self.checkout, pady=12).pack(fill=tk.X, pady=10)

    def show_kasir_page(self):
        # Update button styles
        self.btn_kasir.config(bg="white", fg=self.colors['accent'])
        self.btn_pemasukan.config(bg=self.colors['bg_card'], fg=self.colors['text_gray'])
        
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Header dengan search
        header = tk.Frame(self.content_frame, bg=self.colors['bg_dark'])
        header.pack(fill=tk.X, padx=20, pady=15)
        
        search_frame = tk.Frame(header, bg=self.colors['bg_card'])
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(search_frame, text="🔍", font=("Arial", 12), 
                bg=self.colors['bg_card'], fg="white").pack(side=tk.LEFT, padx=10)
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, font=("Arial", 11), bg=self.colors['bg_card'],
                               fg="white", relief=tk.FLAT, insertbackground="white",
                               textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=12, padx=5)
        
        # Placeholder text
        placeholder_text = "Cari menu..."
        search_entry.insert(0, placeholder_text)
        search_entry.config(fg=self.colors['text_gray'])
        
        def on_focus_in(event):
            if search_entry.get() == placeholder_text:
                search_entry.delete(0, tk.END)
                search_entry.config(fg="white")
        
        def on_focus_out(event):
            if search_entry.get() == "":
                search_entry.insert(0, placeholder_text)
                search_entry.config(fg=self.colors['text_gray'])
        
        search_entry.bind("<FocusIn>", on_focus_in)
        search_entry.bind("<FocusOut>", on_focus_out)
        
        # Icons
        icon_frame = tk.Frame(header, bg=self.colors['bg_dark'])
        icon_frame.pack(side=tk.RIGHT, padx=10)
        
        # Notification icon (clickable)
        notif_btn = tk.Label(icon_frame, text="🔔", font=("Arial", 16), bg=self.colors['bg_dark'],
                            fg="white", cursor="hand2")
        notif_btn.pack(side=tk.LEFT, padx=8)
        notif_btn.bind("<Button-1>", lambda e: self.show_notification_history())
        
        tk.Label(icon_frame, text="👤", font=("Arial", 16), bg=self.colors['bg_dark'],
                fg="white").pack(side=tk.LEFT, padx=8)
        
        # Menu grid dengan scroll
        canvas = tk.Canvas(self.content_frame, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        menu_container = tk.Frame(canvas, bg=self.colors['bg_dark'])
        
        # Bind untuk update scroll region
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        menu_container.bind("<Configure>", on_frame_configure)
        
        # Create window dengan width yang akan di-update
        canvas_window = canvas.create_window((0, 0), window=menu_container, anchor="nw")
        
        # Bind untuk update window width saat canvas resize
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure grid columns untuk 3 kolom
        menu_container.grid_columnconfigure(0, weight=1, uniform="col")
        menu_container.grid_columnconfigure(1, weight=1, uniform="col")
        menu_container.grid_columnconfigure(2, weight=1, uniform="col")
        
        # Store menu cards untuk search
        self.menu_cards = {}
        
        # Create menu cards (3 kolom)
        for idx, item in enumerate(self.menu_items):
            row = idx // 3
            col = idx % 3
            card_widget = self.create_menu_card(menu_container, item, row, col)
            self.menu_cards[item['id']] = {'widget': card_widget, 'item': item}
        
        # Bind search function
        def search_menu(*args):
            search_text = self.search_var.get().lower()
            if search_text == "cari menu...":
                search_text = ""
            
            for item_id, card_data in self.menu_cards.items():
                item_name = card_data['item']['name'].lower()
                if search_text in item_name or search_text == "":
                    card_data['widget'].grid()
                else:
                    card_data['widget'].grid_remove()
        
        self.search_var.trace('w', search_menu)

    def create_menu_card(self, parent, item, row, col):
        # Outer frame untuk rounded effect
        card_outer = tk.Frame(parent, bg=self.colors['bg_dark'], highlightthickness=0)
        card_outer.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")
        
        # Store grid info untuk show/hide
        card_outer.grid_info_stored = {'row': row, 'column': col, 'padx': 12, 'pady': 12, 'sticky': 'nsew'}
        
        card = tk.Frame(card_outer, bg=self.colors['bg_card'], highlightthickness=0)
        card.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Gambar dengan rounded corners
        if item['id'] in self.images:
            img_label = tk.Label(card, image=self.images[item['id']], bg=self.colors['bg_card'])
            img_label.pack(fill=tk.X, pady=0)
        else:
            # Placeholder jika gambar tidak ada
            placeholder = tk.Label(card, text="🍜", font=("Arial", 60),
                                  bg="#333333", fg="white", height=3)
            placeholder.pack(fill=tk.X)
        
        # Info frame dengan relative positioning untuk button
        info_container = tk.Frame(card, bg=self.colors['bg_card'])
        info_container.pack(fill=tk.BOTH, expand=True)
        
        # Text info
        info_frame = tk.Frame(info_container, bg=self.colors['bg_card'])
        info_frame.pack(fill=tk.X, padx=16, pady=(12, 8))
        
        tk.Label(info_frame, text=item['name'], font=("Segoe UI", 13, "bold"),
                bg=self.colors['bg_card'], fg="white", anchor="w").pack(fill=tk.X)
        tk.Label(info_frame, text=f"Rp {item['price']:,}", font=("Segoe UI", 11),
                bg=self.colors['bg_card'], fg=self.colors['text_gray'], 
                anchor="w").pack(fill=tk.X, pady=(4, 0))
        
        # Add button positioned at bottom right
        btn_container = tk.Frame(info_container, bg=self.colors['bg_card'])
        btn_container.pack(fill=tk.X, padx=16, pady=(0, 16))
        
        if item.get("has_variant"):
            add_btn = tk.Button(btn_container, text="+", font=("Arial", 18, "bold"),
                               bg="white", fg="black", relief=tk.FLAT, 
                               width=2, height=1, cursor="hand2",
                               command=lambda i=item: self.show_variant_dialog(i))
        else:
            add_btn = tk.Button(btn_container, text="+", font=("Arial", 18, "bold"),
                               bg="white", fg="black", relief=tk.FLAT,
                               width=2, height=1, cursor="hand2",
                               command=lambda i=item: self.add_to_cart(i))
        add_btn.pack(side=tk.RIGHT)
        
        # Hover effect
        def on_enter(e):
            card.config(bg="#222222")
            info_container.config(bg="#222222")
            info_frame.config(bg="#222222")
            btn_container.config(bg="#222222")
            for child in info_frame.winfo_children():
                child.config(bg="#222222")
        
        def on_leave(e):
            card.config(bg=self.colors['bg_card'])
            info_container.config(bg=self.colors['bg_card'])
            info_frame.config(bg=self.colors['bg_card'])
            btn_container.config(bg=self.colors['bg_card'])
            for child in info_frame.winfo_children():
                child.config(bg=self.colors['bg_card'])
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        if item['id'] in self.images:
            img_label.bind("<Enter>", on_enter)
            img_label.bind("<Leave>", on_leave)
        
        return card_outer

    def show_variant_dialog(self, item):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Pilih Varian")
        dialog.geometry("350x250")
        dialog.configure(bg=self.colors['bg_card'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Header
        header = tk.Frame(dialog, bg=self.colors['bg_card'])
        header.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(header, text="Pilih Metode Pembayaran", font=("Arial", 13, "bold"),
                bg=self.colors['bg_card'], fg="white").pack(side=tk.LEFT)
        tk.Button(header, text="×", font=("Arial", 16), bg=self.colors['bg_card'],
                 fg="white", relief=tk.FLAT, command=dialog.destroy).pack(side=tk.RIGHT)
        
        # Variant buttons
        for variant in item.get("variants", []):
            btn = tk.Button(dialog, text=variant, font=("Arial", 12),
                           bg=self.colors['bg_dark'], fg="white", relief=tk.FLAT,
                           command=lambda v=variant: self.add_variant_and_close(item, v, dialog),
                           pady=15)
            btn.pack(fill=tk.X, padx=20, pady=5)
            
            # Hover effect
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.colors['accent']))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.colors['bg_dark']))
    
    def add_variant_and_close(self, item, variant, dialog):
        item_copy = item.copy()
        item_copy["variant"] = variant
        item_copy["name"] = f"{item['name']} ({variant})"
        self.add_to_cart(item_copy)
        dialog.destroy()
    
    def add_to_cart(self, item):
        item_key = f"{item['id']}_{item.get('variant', '')}"
        
        for cart_item in self.cart:
            if cart_item.get("item_key") == item_key:
                cart_item["quantity"] += 1
                self.update_cart_display()
                # Show notification
                self.show_notification(f"✓ {item['name']} ditambahkan ke keranjang", duration=2000)
                return
        
        self.cart.append({
            "id": item["id"],
            "item_key": item_key,
            "name": item["name"],
            "price": item["price"],
            "quantity": 1,
            "variant": item.get("variant", "")
        })
        self.update_cart_display()
        # Show notification
        self.show_notification(f"✓ {item['name']} ditambahkan ke keranjang", duration=2000)

    def update_cart_display(self):
        for widget in self.cart_items_frame.winfo_children():
            widget.destroy()
        
        if not self.cart:
            tk.Label(self.cart_items_frame, text="Keranjang kosong", font=("Arial", 10),
                    bg=self.colors['bg_card'], fg="#666666").pack(pady=30)
        else:
            for item in self.cart:
                self.create_cart_item(item)
        
        # Update summary
        subtotal = sum(item["price"] * item["quantity"] for item in self.cart)
        tax = subtotal * 0.1
        total = subtotal + tax
        
        self.subtotal_label.config(text=f"Subtotal: Rp {subtotal:,.0f}")
        self.tax_label.config(text=f"Pajak (10%): Rp {tax:,.0f}")
        self.total_label.config(text=f"Total: Rp {total:,.0f}")
    
    def create_cart_item(self, item):
        item_frame = tk.Frame(self.cart_items_frame, bg=self.colors['bg_card'])
        item_frame.pack(fill=tk.X, pady=8)
        
        # Left: Info
        info_frame = tk.Frame(item_frame, bg=self.colors['bg_card'])
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(info_frame, text=item["name"], font=("Arial", 10, "bold"),
                bg=self.colors['bg_card'], fg="white", anchor="w").pack(fill=tk.X)
        tk.Label(info_frame, text=f"Rp {item['price']:,}", font=("Arial", 9),
                bg=self.colors['bg_card'], fg=self.colors['text_gray'], 
                anchor="w").pack(fill=tk.X)
        
        # Quantity controls
        qty_frame = tk.Frame(info_frame, bg=self.colors['bg_card'])
        qty_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(qty_frame, text="-", font=("Arial", 9), bg="#333333", fg="white",
                 relief=tk.FLAT, width=2, command=lambda: self.update_quantity(item, -1)).pack(side=tk.LEFT)
        tk.Label(qty_frame, text=str(item["quantity"]), font=("Arial", 10, "bold"),
                bg=self.colors['bg_card'], fg="white", width=3).pack(side=tk.LEFT, padx=5)
        tk.Button(qty_frame, text="+", font=("Arial", 9), bg="#333333", fg="white",
                 relief=tk.FLAT, width=2, command=lambda: self.update_quantity(item, 1)).pack(side=tk.LEFT)
        
        # Right: Remove button
        tk.Button(item_frame, text="×", font=("Arial", 14), bg=self.colors['accent'],
                 fg="white", relief=tk.FLAT, width=2,
                 command=lambda: self.remove_from_cart(item)).pack(side=tk.RIGHT)
    
    def update_quantity(self, item, change):
        item["quantity"] += change
        if item["quantity"] <= 0:
            self.cart.remove(item)
        self.update_cart_display()
    
    def remove_from_cart(self, item):
        self.cart.remove(item)
        self.update_cart_display()
    
    def clear_cart(self):
        if messagebox.askyesno("Konfirmasi", "Hapus semua item dari keranjang?"):
            self.cart = []
            self.update_cart_display()

    def checkout(self):
        if not self.cart:
            messagebox.showwarning("Peringatan", "Keranjang masih kosong!")
            return
        
        subtotal = sum(item["price"] * item["quantity"] for item in self.cart)
        tax = subtotal * 0.1
        total = subtotal + tax
        
        # Payment dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Pilih Metode Pembayaran")
        dialog.geometry("450x600")
        dialog.configure(bg=self.colors['bg_card'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Header
        header = tk.Frame(dialog, bg=self.colors['bg_card'])
        header.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(header, text="Pilih Metode Pembayaran", font=("Arial", 14, "bold"),
                bg=self.colors['bg_card'], fg="white").pack(side=tk.LEFT)
        tk.Button(header, text="×", font=("Arial", 18), bg=self.colors['bg_card'],
                 fg="white", relief=tk.FLAT, command=dialog.destroy).pack(side=tk.RIGHT)
        
        # Summary
        summary = tk.Frame(dialog, bg=self.colors['bg_dark'])
        summary.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(summary, text=f"Subtotal: Rp {subtotal:,.0f}", font=("Arial", 10),
                bg=self.colors['bg_dark'], fg="white", anchor="w").pack(fill=tk.X, padx=15, pady=3)
        tk.Label(summary, text=f"Pajak (10%): Rp {tax:,.0f}", font=("Arial", 10),
                bg=self.colors['bg_dark'], fg="white", anchor="w").pack(fill=tk.X, padx=15, pady=3)
        tk.Label(summary, text=f"Total Bayar: Rp {total:,.0f}", font=("Arial", 14, "bold"),
                bg=self.colors['bg_dark'], fg="white", anchor="w").pack(fill=tk.X, padx=15, pady=8)
        
        # Payment methods
        payment_var = tk.StringVar(value="cash")
        
        methods_frame = tk.Frame(dialog, bg=self.colors['bg_card'])
        methods_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        methods = [
            ("💵 Tunai", "cash"),
            ("💳 Kartu Debit", "debit"),
            ("💳 Kartu Kredit", "credit"),
            ("📱 E-Wallet", "ewallet"),
            ("📲 QRIS", "qris"),
            ("🏦 Transfer Bank", "transfer")
        ]
        
        for text, value in methods:
            rb = tk.Radiobutton(methods_frame, text=text, variable=payment_var, value=value,
                               font=("Arial", 11), bg=self.colors['bg_card'], fg="white",
                               selectcolor="#333333", activebackground=self.colors['bg_card'],
                               activeforeground="white", anchor="w", padx=10, pady=8)
            rb.pack(fill=tk.X, pady=3)
        
        # Confirm button
        tk.Button(dialog, text="Konfirmasi Pembayaran", font=("Arial", 12, "bold"),
                 bg=self.colors['accent'], fg="white", relief=tk.FLAT, pady=12,
                 command=lambda: self.process_payment(payment_var.get(), total, dialog)).pack(
                 fill=tk.X, padx=20, pady=20)

    def process_payment(self, method, total, dialog):
        if method == "cash":
            cash_dialog = tk.Toplevel(dialog)
            cash_dialog.title("Pembayaran Tunai")
            cash_dialog.geometry("400x300")
            cash_dialog.configure(bg=self.colors['bg_card'])
            cash_dialog.transient(dialog)
            cash_dialog.grab_set()
            
            tk.Label(cash_dialog, text="Pembayaran Tunai", font=("Arial", 14, "bold"),
                    bg=self.colors['bg_card'], fg="white").pack(pady=20)
            
            tk.Label(cash_dialog, text=f"Total: Rp {total:,.0f}", font=("Arial", 12),
                    bg=self.colors['bg_card'], fg="white").pack(pady=10)
            
            tk.Label(cash_dialog, text="Masukkan jumlah uang:", font=("Arial", 11),
                    bg=self.colors['bg_card'], fg="white").pack(pady=5)
            
            cash_entry = tk.Entry(cash_dialog, font=("Arial", 14), bg=self.colors['bg_dark'],
                                 fg="white", justify="center", insertbackground="white")
            cash_entry.pack(pady=10, padx=40, fill=tk.X)
            cash_entry.focus()
            
            change_label = tk.Label(cash_dialog, text="Kembalian: Rp 0", font=("Arial", 12, "bold"),
                                   bg=self.colors['bg_card'], fg="#4CAF50")
            change_label.pack(pady=10)
            
            def calculate_change(*args):
                try:
                    cash = int(cash_entry.get())
                    change = cash - total
                    if change >= 0:
                        change_label.config(text=f"Kembalian: Rp {change:,.0f}", fg="#4CAF50")
                    else:
                        change_label.config(text=f"Kurang: Rp {abs(change):,.0f}", fg=self.colors['accent'])
                except:
                    change_label.config(text="Kembalian: Rp 0", fg="#4CAF50")
            
            cash_entry.bind("<KeyRelease>", calculate_change)
            
            def confirm_cash():
                try:
                    cash = int(cash_entry.get())
                    if cash < total:
                        messagebox.showerror("Error", f"Uang tidak cukup!\nKurang: Rp {total - cash:,.0f}")
                        return
                    cash_dialog.destroy()
                    self.finalize_payment(method, total, cash, dialog)
                except:
                    messagebox.showerror("Error", "Masukkan jumlah uang yang valid!")
            
            tk.Button(cash_dialog, text="Konfirmasi", font=("Arial", 12, "bold"),
                     bg=self.colors['accent'], fg="white", relief=tk.FLAT, pady=10,
                     command=confirm_cash).pack(fill=tk.X, padx=40, pady=20)
        else:
            self.finalize_payment(method, total, 0, dialog)
    
    def finalize_payment(self, method, total, cash_amount, dialog):
        transaction = {
            "id": datetime.now().strftime('%Y%m%d%H%M%S'),
            "items": self.cart.copy(),
            "total": total,
            "payment_method": method,
            "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.transactions.append(transaction)
        self.save_transactions()
        
        dialog.destroy()
        
        payment_names = {
            'cash': 'Tunai', 'debit': 'Kartu Debit', 'credit': 'Kartu Kredit',
            'ewallet': 'E-Wallet', 'qris': 'QRIS', 'transfer': 'Transfer Bank'
        }
        
        receipt = f"✓ Pembayaran Berhasil!\n\n"
        receipt += f"ID Transaksi: {transaction['id']}\n"
        receipt += f"Metode: {payment_names[method]}\n"
        receipt += f"Total: Rp {total:,.0f}\n"
        
        if method == "cash" and cash_amount > 0:
            change = cash_amount - total
            receipt += f"\nUang Tunai: Rp {cash_amount:,.0f}\n"
            receipt += f"Kembalian: Rp {change:,.0f}\n"
        
        receipt += "\nTerima kasih atas pembelian Anda!"
        
        # Show messagebox
        messagebox.showinfo("Pembayaran Berhasil", receipt)
        
        # Show notification
        notif_message = f"Pesanan berhasil dibayar! ID: {transaction['id']}"
        self.show_notification(notif_message, duration=4000, type="success")
        
        self.cart = []
        self.update_cart_display()

    def show_pemasukan_page(self):
        self.btn_kasir.config(bg=self.colors['bg_card'], fg=self.colors['text_gray'])
        self.btn_pemasukan.config(bg="white", fg=self.colors['accent'])
        
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.content_frame, text="Laporan Pemasukan", font=("Arial", 20, "bold"),
                bg=self.colors['bg_dark'], fg="white").pack(pady=20, padx=20, anchor="w")
        
        # Stats cards
        stats_frame = tk.Frame(self.content_frame, bg=self.colors['bg_dark'])
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        total_income = sum(t["total"] for t in self.transactions)
        total_trans = len(self.transactions)
        avg_trans = total_income / total_trans if total_trans > 0 else 0
        
        self.create_stat_card(stats_frame, "💵", "Total Pemasukan Hari Ini", 
                             f"Rp {total_income:,.0f}", 0)
        self.create_stat_card(stats_frame, "🛒", "Total Transaksi", str(total_trans), 1)
        self.create_stat_card(stats_frame, "📈", "Rata-rata Transaksi", 
                             f"Rp {avg_trans:,.0f}", 2)
        
        # Table
        table_frame = tk.Frame(self.content_frame, bg=self.colors['bg_card'])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(table_frame, text="Riwayat Transaksi", font=("Arial", 14, "bold"),
                bg=self.colors['bg_card'], fg="white").pack(pady=15, padx=20, anchor="w")
        
        # Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=self.colors['bg_dark'], 
                       foreground="white", fieldbackground=self.colors['bg_dark'],
                       borderwidth=0)
        style.configure("Treeview.Heading", background=self.colors['bg_card'],
                       foreground="white", borderwidth=0)
        style.map("Treeview", background=[("selected", self.colors['accent'])])
        
        tree = ttk.Treeview(table_frame, columns=("ID", "Tanggal", "Item", "Metode", "Total"),
                           show="headings", height=15)
        
        tree.heading("ID", text="ID Transaksi")
        tree.heading("Tanggal", text="Tanggal & Waktu")
        tree.heading("Item", text="Item")
        tree.heading("Metode", text="Metode Bayar")
        tree.heading("Total", text="Total")
        
        tree.column("ID", width=120)
        tree.column("Tanggal", width=150)
        tree.column("Item", width=250)
        tree.column("Metode", width=120)
        tree.column("Total", width=120)
        
        payment_names = {
            'cash': 'Tunai', 'debit': 'Kartu Debit', 'credit': 'Kartu Kredit',
            'ewallet': 'E-Wallet', 'qris': 'QRIS', 'transfer': 'Transfer Bank'
        }
        
        for trans in reversed(self.transactions):
            items_text = ", ".join([f"{item['name']} ({item['quantity']}x)" 
                                   for item in trans['items']])
            tree.insert("", "end", values=(
                trans["id"],
                trans["date"],
                items_text[:40] + "..." if len(items_text) > 40 else items_text,
                payment_names.get(trans["payment_method"], trans["payment_method"]),
                f"Rp {trans['total']:,.0f}"
            ))
        
        tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    def create_stat_card(self, parent, icon, title, value, col):
        card = tk.Frame(parent, bg=self.colors['bg_card'])
        card.grid(row=0, column=col, padx=10, pady=10, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)
        
        tk.Label(card, text=icon, font=("Arial", 36), bg=self.colors['bg_dark'],
                fg="white").pack(pady=15)
        tk.Label(card, text=title, font=("Arial", 10), bg=self.colors['bg_card'],
                fg=self.colors['text_gray']).pack()
        tk.Label(card, text=value, font=("Arial", 18, "bold"), bg=self.colors['bg_card'],
                fg="white").pack(pady=10)
    
    def load_transactions(self):
        if os.path.exists("transactions.json"):
            with open("transactions.json", "r") as f:
                return json.load(f)
        return []
    
    def save_transactions(self):
        with open("transactions.json", "w") as f:
            json.dump(self.transactions, f, indent=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = KedaiHaunaApp(root)
    root.mainloop()
