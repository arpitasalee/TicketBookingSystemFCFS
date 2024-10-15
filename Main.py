import customtkinter as ctk
from tkinter import messagebox, ttk, Toplevel, Entry, Label
import random
import threading
import time
import sqlite3

# Function to process the queue (simulating FCFS scheduling)
def process_queue():
    global QUEUE
    while True:
        if QUEUE:
            user_id = QUEUE.pop(0)  # Process the first in queue
            result = book_ticket(user_id)
            update_queue_status(f"{result}")  # Update the status
            app.update_queue_label()  # Update queue label and progress bar after booking
            
            # If the queue hits zero, open the seat selection window
            if not QUEUE:
                app.open_seat_selection_window()
        time.sleep(2)

def book_ticket(user_id):
    conn = sqlite3.connect('ticket_booking.db')
    cursor = conn.cursor()

    # Check if tickets are available
    cursor.execute("SELECT ticket_id FROM tickets WHERE is_booked = 0 LIMIT 1")
    available_ticket = cursor.fetchone()

    if available_ticket:
        ticket_id = available_ticket[0]
        cursor.execute("UPDATE tickets SET is_booked = 1 WHERE ticket_id = ?", (ticket_id,))
        conn.commit()
        conn.close()
        return f"Booking successful for User {user_id}. Ticket ID: {ticket_id}"
    else:
        conn.close()
        return f"Booking failed for User {user_id}. No tickets available."

# Updating queue status in the status bar
def update_queue_status(status):
    status_label.configure(text=status)

# GUI Application for a Sophisticated Ticket Booking System
class TicketBookingApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Concert Ticket Booking System")
        self.root.geometry("600x400")
        self.root.config(bg="#2E2E2E")  # Dark background color

        # Main content frame
        self.main_frame = ctk.CTkFrame(self.root, fg_color="#2E2E2E")
        self.main_frame.pack(fill="both", expand=True)

        # Centering the frame
        self.main_frame.place(relx=0.5, rely=0.5, anchor='center')

        # Queue Label
        self.queue_label = ctk.CTkLabel(self.main_frame, text="People in Queue: 0", font=("Helvetica", 12), fg_color="#2E2E2E", text_color="white")
        self.queue_label.pack(pady=10)

        # Join Queue Button
        self.join_button = ctk.CTkButton(self.main_frame, text="Join Queue", command=self.join_queue, font=("Helvetica", 14),
                                          fg_color="#28a745", text_color="white", width=200)
        self.join_button.pack(pady=10)

        # Progress Bar for the queue
        self.progress = ttk.Progressbar(self.main_frame, length=300, mode='determinate')
        self.progress.pack(pady=10)

        # Queue Position Label
        self.position_label = ctk.CTkLabel(self.main_frame, text="", font=("Helvetica", 10), fg_color="#2E2E2E", text_color="white")
        self.position_label.pack(pady=5)

        # Status Bar
        self.status_frame = ctk.CTkFrame(self.root, fg_color="#343a40")
        self.status_frame.pack(side="bottom", fill="x")
        global status_label
        status_label = ctk.CTkLabel(self.status_frame, text="Welcome to Concert Ticket Booking", fg_color="#343a40", text_color="white",
                                     font=("Helvetica", 10))
        status_label.pack(padx=10, pady=5)

    def join_queue(self):
        user_id = random.randint(1000, 9999)  # Assign a random user ID
        QUEUE.append(user_id)
        messagebox.showinfo("Success", f"You are in the queue! Your User ID: {user_id}")
        self.update_queue_label()  # Update queue label and progress bar
        self.join_button.configure(state='disabled')  # Disable the button after click

    def update_queue_label(self):
        queue_length = len(QUEUE)
        self.queue_label.configure(text=f"People in Queue: {queue_length}")
        self.update_progress_bar(queue_length)  # Update progress bar when the queue label updates

    def update_progress_bar(self, queue_length):
        self.progress['value'] = queue_length  # Update the progress bar based on queue length
        self.progress['maximum'] = 100  # Assuming 100 is the ticket limit

    def open_seat_selection_window(self):
        self.seat_selection_window = TicketBookingSystem(ctk.CTk())
        self.seat_selection_window.root.mainloop()  # Open seat selection window

# Seat selection system
class TicketBookingSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Ticket Booking System (Seat Selection)")
        self.root.geometry("600x400")  # Set window size

        # Set appearance mode to "dark"
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Initialize seat data (10 seats available, 4x5 grid)
        self.rows = 4
        self.columns = 5
        self.seats = [[f"{r * self.columns + c + 1}" for c in range(self.columns)] for r in range(self.rows)]
        self.selected_seats = []  # List to store selected seats
        self.default_color = "#1f6aa5"  # Set default color to the specified value

        # UI Components
        self.create_widgets()

    def create_widgets(self):
        # Label for seat availability
        self.label_seats = ctk.CTkLabel(self.root, text="Choose Your Seats", font=("Arial", 16))
        self.label_seats.grid(row=0, column=0, columnspan=self.columns, pady=(10, 5))  # Center label

        # Create seat buttons in a grid and center the grid
        self.seat_buttons = []
        for r in range(self.rows):
            row_buttons = []
            for c in range(self.columns):
                seat_text = self.seats[r][c]
                btn = ctk.CTkButton(self.root, text=seat_text, width=80, height=40,
                                    command=lambda r=r, c=c: self.toggle_seat(r, c))
                btn.grid(row=r + 1, column=c, padx=5, pady=5)  # Use grid here
                row_buttons.append(btn)
            self.seat_buttons.append(row_buttons)

        # Create a frame for the Next and Reset buttons
        self.button_frame = ctk.CTkFrame(self.root)
        self.button_frame.grid(row=self.rows + 1, column=0, columnspan=self.columns, pady=10)

        # Add "Res" button to reset selections
        self.reset_button = ctk.CTkButton(self.button_frame, text="Res", command=self.reset_selections, 
                                            font=("Arial", 12), fg_color="red", width=50)
        self.reset_button.grid(row=0, column=0, padx=(0, 10), sticky="e")  # Place "Res" button on the left

        # Add "Next" button
        self.next_button = ctk.CTkButton(self.button_frame, text="Next", command=self.go_to_next_step, font=("Arial", 12))
        self.next_button.grid(row=0, column=1, sticky="e")  # Place "Next" button next to "Res"

        # Make the grid responsive
        for i in range(self.rows + 2):
            self.root.grid_rowconfigure(i, weight=1)
        for j in range(self.columns):
            self.root.grid_columnconfigure(j, weight=1)

    def toggle_seat(self, row, col):
        selected_seat = self.seats[row][col]
        if selected_seat in self.selected_seats:
            self.selected_seats.remove(selected_seat)  # Deselect the seat
            self.reset_seat(selected_seat)
        else:
            self.selected_seats.append(selected_seat)  # Select the seat
            self.highlight_seat(selected_seat)

    def highlight_seat(self, seat):
        # Highlight the selected seat button
        for row_buttons in self.seat_buttons:
            for btn in row_buttons:
                if btn.cget("text") == seat:
                    btn.configure(fg_color="green")  # Change color to indicate selection

    def reset_seat(self, seat):
        # Reset the previous seat's button color to default
        for row_buttons in self.seat_buttons:
            for btn in row_buttons:
                if btn.cget("text") == seat:
                    btn.configure(fg_color=self.default_color)  # Change back to default color

    def reset_selections(self):
        # Reset all selected seats and button colors
        for selected_seat in self.selected_seats:
            self.reset_seat(selected_seat)  # Reset individual seat color
       
    def reset_selections(self):
        # Reset all selected seats and button colors
        for selected_seat in self.selected_seats:
            self.reset_seat(selected_seat)  # Reset individual seat color
        self.selected_seats.clear()  # Clear the list of selected seats

    def go_to_next_step(self):
        # Handle the action when "Next" is clicked
        if self.selected_seats:
            # Open a popup to collect user details
            self.open_user_details_popup()
        else:
            messagebox.showwarning("No Selection", "Please select at least one seat before proceeding.")

    def open_user_details_popup(self):
        popup = Toplevel(self.root)  # Create a new window
        popup.title("User Details")
        popup.geometry("300x200")  # Set the size of the popup

        # Name Label and Entry
        Label(popup, text="Name:").pack(pady=(10, 0))
        name_entry = Entry(popup)
        name_entry.pack(pady=(0, 10))

        # Username Label and Entry
        Label(popup, text="Username:").pack(pady=(10, 0))
        username_entry = Entry(popup)
        username_entry.pack(pady=(0, 10))

        # Submit Button
        submit_button = ctk.CTkButton(popup, text="Submit", command=lambda: self.submit_user_details(popup, name_entry.get(), username_entry.get()))
        submit_button.pack(pady=10)

    def submit_user_details(self, popup, name, username):
        # Handle the submitted user details
        if name and username:
            messagebox.showinfo("User Details", f"Name: {name}\nUsername: {username}\nSelected Seats: {', '.join(self.selected_seats)}")
            popup.destroy()  # Close the popup
            # Here you can add additional functionality, such as saving user details or proceeding to the next step
        else:
            messagebox.showwarning("Input Error", "Please enter both name and username.")

# Create the main window
if __name__ == "__main__":
    # Queue initialization with 5 random people
    QUEUE = [random.randint(1000, 9999) for _ in range(5)]

    # CustomTkinter window creation
    root = ctk.CTk()  # Change from Tk to CTk for customtkinter
    app = TicketBookingApp(root)

    # Start the thread to process the queue (FCFS)
    threading.Thread(target=process_queue, daemon=True).start()

    root.mainloop()
