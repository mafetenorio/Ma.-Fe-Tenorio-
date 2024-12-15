import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import sys  # Import sys to use sys.exit()

# Function to create the database and tables
def create_db():
    conn = sqlite3.connect("reservations.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS reservations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        email TEXT,
                        phone TEXT,
                        fitness_class TEXT,
                        instructor TEXT,
                        time TEXT)''')
    
    # Create instructors table
    cursor.execute('''CREATE TABLE IF NOT EXISTS instructors (
                        instructor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        available_time TEXT,
                        expertise_area TEXT)''')
    
    conn.commit()
    conn.close()

# Function to populate instructors table with sample data
def add_sample_instructors():
    conn = sqlite3.connect("reservations.db")
    cursor = conn.cursor()
    
    # Define the sample instructors
    instructors = [
        ("Jane Hernandez", "8:00 AM-9:00 AM", "Yoga"),
        ("Sarah Lee", "10:00 AM-11:00 AM", "Yoga"),
        ("Thea Samson", "2:00 PM-3:00 PM", "Pilates"),
        ("Mike Johnson", "4:00 PM-5:00 PM", "Pilates"),
        ("Anna Garcia", "8:00 AM-9:00 AM", "Zumba"),
        ("Karen Mendoza", "10:00 AM-11:00 AM", "Zumba")
    ]
    
    for instructor in instructors:
        # Check if the instructor already exists in the database
        cursor.execute("SELECT COUNT(*) FROM instructors WHERE name = ? AND available_time = ? AND expertise_area = ?", 
                       (instructor[0], instructor[1], instructor[2]))
        count = cursor.fetchone()[0]
        
        if count == 0:  # If the instructor does not exist, insert it
            cursor.execute("INSERT INTO instructors (name, available_time, expertise_area) VALUES (?, ?, ?)", instructor)
    
    conn.commit()
    conn.close()


# Update the instructor combobox based on the selected fitness class
def update_instructors(event=None):
    selected_class = class_combobox.get()

    if selected_class == "Select Class":
        instructor_combobox['values'] = ["Select Instructor"]
        instructor_combobox.set("Select Instructor")
        return

    # Connect to the database to fetch unique instructors for the selected class
    conn = sqlite3.connect("reservations.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT DISTINCT name FROM instructors WHERE expertise_area = ?''', (selected_class,))
    instructors = cursor.fetchall()
    conn.close()

    if instructors:
        instructor_names = ["Select Instructor"] + [instructor[0] for instructor in instructors]
        instructor_combobox['values'] = instructor_names
    else:
        instructor_combobox['values'] = ["Select Instructor"]
    
    instructor_combobox.set("Select Instructor")

# Add a reservation to the database
def add_reservation():
    name = name_entry.get()
    email = email_entry.get()
    phone = phone_entry.get()
    fitness_class = class_combobox.get()
    instructor = instructor_combobox.get()
    time = time_combobox.get()
    
    if not name or not email or not phone or fitness_class == "Select Class" or instructor == "Select Instructor" or time == "Select Time":
        messagebox.showwarning("Input Error", "Please fill in all fields.")
        return

    conn = sqlite3.connect("reservations.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reservations (name, email, phone, fitness_class, instructor, time) VALUES (?, ?, ?, ?, ?, ?)",
                   (name, email, phone, fitness_class, instructor, time))
    conn.commit()
    conn.close()
    
    reservations_tree.insert("", "end", values=(name, email, phone, fitness_class, instructor, time))
    name_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)
    class_combobox.set("Select Class")
    instructor_combobox.set("Select Instructor")
    time_combobox.set("Select Time")

    display_reservations()

def delete_reservation():
    # Get the selected item from the Treeview
    selected_item = reservations_tree.selection()

    if not selected_item:  # If no row is selected, show a message
        messagebox.showwarning("No Selection", "Please select a reservation to delete.")
        return

    # Get the values of the selected row
    selected_values = reservations_tree.item(selected_item, "values")

    # Assuming the 'id' is stored as a tag in the Treeview item.
    selected_id = reservations_tree.item(selected_item, "tags")[0]  # Fetch the 'id' tag

    # Confirm deletion from the user
    confirm = messagebox.askyesno("Delete Confirmation", f"Are you sure you want to delete reservation {selected_values[0]}?")
    
    if confirm:
        # Connect to the database and delete the record using the id
        conn = sqlite3.connect("reservations.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reservations WHERE id = ?", (selected_id,))
        conn.commit()
        conn.close()
        
        # Refresh the Treeview to remove the deleted row
        reservations_tree.delete(selected_item)
        messagebox.showinfo("Deleted", "Reservation deleted successfully.")

     
def update_reservation():
    selected_item = reservations_tree.selection()
    
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select a reservation to update.")
        return
    
    # Get the current values of the selected reservation
    reservation = reservations_tree.item(selected_item)["values"]
    
    # Populate the entry fields with the selected reservation's data
    name_entry.delete(0, tk.END)
    name_entry.insert(0, reservation[0])
    
    email_entry.delete(0, tk.END)
    email_entry.insert(0, reservation[1])
    
    phone_entry.delete(0, tk.END)
    phone_entry.insert(0, reservation[2])
    
    class_combobox.set(reservation[3])
    update_instructors()  # This updates the instructor list based on the selected class
    instructor_combobox.set(reservation[4])
    
    time_combobox.set(reservation[5])
    
    # Perform the update directly when the update button is clicked
    def perform_update():
        # Update the reservation in the database
        selected_id = reservations_tree.item(selected_item, "tags")[0]  # Fetch the 'id' tag
        conn = sqlite3.connect("reservations.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE reservations SET name = ?, email = ?, phone = ?, fitness_class = ?, instructor = ?, time = ? WHERE id = ?",
                       (name_entry.get(), email_entry.get(), phone_entry.get(), class_combobox.get(), instructor_combobox.get(), time_combobox.get(), selected_id))  # Use the id for the update
        conn.commit()
        conn.close()

        # Clear the entry fields
        name_entry.delete(0, tk.END)
        email_entry.delete(0, tk.END)
        phone_entry.delete(0, tk.END)
        class_combobox.set("Select Class")
        instructor_combobox.set("Select Instructor")
        time_combobox.set("Select Time")
        messagebox.showinfo("Success", "Reservation updated successfully!")

        # Refresh the Treeview to show the updated reservation
        display_reservations()

    # Bind the perform_update function to the update button
    update_button.config(command=perform_update)

def display_reservations():
    # Clear the current treeview entries
    for item in reservations_tree.get_children():
        reservations_tree.delete(item)

    # Fetch all reservations from the database
    conn = sqlite3.connect("reservations.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, phone, fitness_class, instructor, time FROM reservations")  # Include id
    rows = cursor.fetchall()
    conn.close()

    # Insert the fetched reservations into the treeview
    for row in rows:
        reservations_tree.insert("", "end", values=row[1:], tags=(row[0],))  # Store the id as a tag


# Show the reservation window
def show_reservation_window():
    login_frame.grid_forget()  # Hide login frame
    reservation_frame.grid(row=0, column=0, padx=20, pady=20)  # Show reservation frame

# Show the login window
def show_login_window():
    login_frame.grid(row=0, column=0, padx=20, pady=20)  # Show login frame
    reservation_frame.grid_forget()  # Hide reservation frame
    
def on_exit():
    # Show a "Thank You" message before exiting the app
    messagebox.showinfo("Thank You", "Thank you for using the Fitness Class Reservation System!")
    
    # After the message, exit the application
    sys.exit()
    
def show_admin_window():
    login_frame.grid_forget()  # Hide login frame
    login_frame.grid(row=0, column=0, padx=20, pady=20)  # Show admin frame

    # Clear the existing widgets in the admin_frame
    for widget in login_frame.winfo_children():
        widget.destroy()

    # Admin Panel for customer, instructor, and class info
    tk.Label(login_frame, text="Admin System", font=("Times", 30, "bold"), bg="lightblue").grid(row=0, column=1, pady=15)

    # Frame to hold the buttons on the left side
    left_frame = tk.Frame(login_frame, width=200)
    left_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

    # Frame to display the information (customer, instructor, or class info)
    info_frame = tk.Frame(login_frame)
    info_frame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")

    # Ensure the info_frame resizes properly to fill the space
    login_frame.grid_rowconfigure(1, weight=1)  # Allow row 1 to expand vertically
    login_frame.grid_columnconfigure(1, weight=1)  # Allow column 1 to expand horizontally

    # Ensure left_frame takes the necessary space for buttons
    login_frame.grid_rowconfigure(1, weight=1)
    login_frame.grid_columnconfigure(0, weight=0)

    # Button functions to show customer, instructor, or class info
    def show_customer_info():
        # Clear any existing content in the info display area
        for widget in info_frame.winfo_children():
            widget.grid_forget()

        # **Customer Information Tab**
        customer_columns = ("Name", "Email", "Phone", "Class", "Instructor", "Time")
        customer_tree = ttk.Treeview(info_frame, columns=customer_columns, show="headings", height=15)
        customer_tree.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        for col in customer_columns:
            customer_tree.heading(col, text=col)
            customer_tree.column(col, width=150, anchor="center")

        # Fetch data from the database for reservations
        conn = sqlite3.connect("reservations.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, phone, fitness_class, instructor, time FROM reservations")
        rows = cursor.fetchall()
        conn.close()

        if rows:  # Only insert data if available
            for row in rows:
                customer_tree.insert("", "end", values=row[1:], iid=row[0])  # row[0] is id, rest is values
        else:
            customer_tree.insert("", "end", values=("No data",) * 6)

    def show_instructor_info():
        # Clear any existing content in the info display area
        for widget in info_frame.winfo_children():
            widget.grid_forget()

        # **Instructor Information Tab**
        instructor_columns = ("Name", "Expertise Area", "Available Time")
        instructor_tree = ttk.Treeview(info_frame, columns=instructor_columns, show="headings", height=15)
        instructor_tree.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        for col in instructor_columns:
            instructor_tree.heading(col, text=col)
            instructor_tree.column(col, width=200, anchor="center")  # Adjusted width for better fitting
            
        # Adjust column widths for better fitting
        instructor_tree.column("Name", width=300, anchor="center")
        instructor_tree.column("Expertise Area", width=300, anchor="center")
        instructor_tree.column("Available Time", width=300, anchor="center") 

        # Fetch instructor data
        conn = sqlite3.connect("reservations.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, expertise_area, available_time FROM instructors")
        instructors = cursor.fetchall()
        conn.close()

        if instructors:  # Insert data if instructors available
            for instructor in instructors:
                instructor_tree.insert("", "end", values=instructor)
        else:
            instructor_tree.insert("", "end", values=("No instructors",) * 3)

    def show_class_info():
        # Clear any existing content in the info display area
        for widget in info_frame.winfo_children():
            widget.grid_forget()

        # Class Information Tab
        class_columns = ("Class Name", "Schedule")
        class_tree = ttk.Treeview(info_frame, columns=class_columns, show="headings", height=15)
        class_tree.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Adjust column widths to ensure text fits
        class_tree.column("Class Name", width=400, anchor="center")
        class_tree.column("Schedule", width=400, anchor="center") 

        for col in class_columns:
            class_tree.heading(col, text=col)

        # Static class data
        classes = [
            ("Yoga", "8:00 AM - 2:00 PM"),
            ("Pilates", "8:30:00 AM - 3:00 PM"),
            ("Zumba", "8:00 AM - 5:00 PM")
        ]

        for class_info in classes:
            class_tree.insert("", "end", values=class_info)

    # Buttons to control which information to display
    customer_button = tk.Button(left_frame, text="Customer Info", command=show_customer_info, width=20, font=("Arial", 14))
    customer_button.grid(row=0, column=0, pady=10, padx=10, sticky="w")

    instructor_button = tk.Button(left_frame, text="Instructor Info", command=show_instructor_info, width=20, font=("Arial", 14))
    instructor_button.grid(row=1, column=0, pady=10, padx=10, sticky="w")

    class_button = tk.Button(left_frame, text="Class Info", command=show_class_info, width=20, font=("Arial", 14))
    class_button.grid(row=2, column=0, pady=10, padx=10, sticky="w")

    # Exit button placed below the class_button
    exit_button = tk.Button(left_frame, text="Exit", command=on_exit, width=20, font=("Arial", 14))
    exit_button.grid(row=3, column=0, pady=10, padx=10, sticky="w")
    

    # Initially show the Customer Info by default
    show_customer_info()  



# Initialize the main application window
root = tk.Tk()
root.title("Fitness Class Reservation System")
root.geometry("1000x700")
root.config(bg="lightblue")

# Create the database
create_db()

# Add sample instructors to the database (for demonstration purposes)
add_sample_instructors()


style = ttk.Style()
style.configure("MediumButton.TButton",
                font=("Arial", 14, "bold"), 
                padding=15,  # Padding to make buttons bigger
                background="lightcoral")  # Set background color of buttons

# Frame for Login Window
login_frame = tk.Frame(root, bg="lightblue")
login_frame.grid(row=0, column=0, padx=20, pady=20)

# WELCOME label below the title
welcome_label1 = tk.Label(login_frame, text="WELCOME", font=("Times", 45, "bold"), bg="lightblue")
welcome_label1.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")  # Centered in grid, spans 2 columns

# FITNESS CLASS RESERVATION SYSTEM label
welcome_label2 = tk.Label(login_frame, text="FITNESS CLASS RESERVATION SYSTEM", font=("Times", 45, "bold"), bg="lightblue")
welcome_label2.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")  # Centered in grid, spans 2 columns

# Frame for centering the buttons
button_frame = tk.Frame(login_frame, bg="lightblue")
button_frame.grid(row=2, column=0, columnspan=2, pady=20)  # Centered by grid

# Admin and User Buttons (Centered within button_frame)
admin_button = ttk.Button(button_frame, text="Admin", width=20, command=show_admin_window, style="MediumButton.TButton")
admin_button.grid(row=0, column=0, padx=10, pady=10)

user_button = ttk.Button(button_frame, text="User", width=20, command=show_reservation_window, style="MediumButton.TButton")
user_button.grid(row=0, column=1, padx=10, pady=10)

# Ensure everything in the login_frame is centered
login_frame.grid_rowconfigure(0, weight=1, minsize=50)  # Add space for the title
login_frame.grid_rowconfigure(1, weight=1, minsize=50)  # Add space for the title
login_frame.grid_rowconfigure(2, weight=1, minsize=50)  # Space for button
login_frame.grid_columnconfigure(0, weight=1)  # Center the buttons

# Frame for Reservations (User Interaction)
reservation_frame = tk.Frame(root, bg="lightblue")
reservation_frame.grid(row=0, column=0, padx=20, pady=20)

# Frame for Reservation System (Hidden initially)
reservation_frame = tk.Frame(root, bg="lightblue")

# Frame for Customer Information (Left side)
left_frame = tk.Frame(reservation_frame, padx=25, pady=25, bg="lightyellow")
left_frame.grid(row=0, column=0, padx=25, pady=25)

# Customer Information Section
tk.Label(left_frame, text="Customer Information", font=("Times", 20), bg="lightyellow").grid(row=0, column=0, columnspan=2, pady=15)

tk.Label(left_frame, text="Name:", font=("Arial", 12), bg="lightyellow").grid(row=1, column=0, sticky="w", pady=5)
name_entry = tk.Entry(left_frame, width=58, bg="white")  
name_entry.grid(row=1, column=1, pady=5)

tk.Label(left_frame, text="Email:", font=("Arial", 12), bg="lightyellow").grid(row=2, column=0, sticky="w", pady=5)
email_entry = tk.Entry(left_frame, width=58, bg="white")
email_entry.grid(row=2, column=1, pady=5)

tk.Label(left_frame, text="Phone:", font=("Arial", 12), bg="lightyellow").grid(row=3, column=0, sticky="w", pady=5)
phone_entry = tk.Entry(left_frame, width=58, bg="white")
phone_entry.grid(row=3, column=1, pady=5)

# Fitness Class Reservation Section
tk.Label(left_frame, text="Fitness Class Reservation", font=("Times", 20), bg="lightyellow").grid(row=4, column=0, columnspan=2, pady=10)

tk.Label(left_frame, text="Class:", font=("Arial", 12), bg="lightyellow").grid(row=5, column=0, sticky="w", pady=5)
class_combobox = ttk.Combobox(left_frame, values=["Select Class", "Yoga", "Pilates", "Zumba"], font=("Arial", 10), width=48)
class_combobox.set("Select Class")
class_combobox.grid(row=5, column=1, pady=5)
class_combobox.bind("<<ComboboxSelected>>", update_instructors)  # Bind the event to update instructors

tk.Label(left_frame, text="Instructor:", font=("Arial", 12), bg="lightyellow").grid(row=6, column=0, sticky="w", pady=10)
instructor_combobox = ttk.Combobox(left_frame, values=["Select Instructor"], font=("Arial", 10), width=48)
instructor_combobox.set("Select Instructor")
instructor_combobox.grid(row=6, column=1, pady=6)

tk.Label(left_frame, text="Time:", font=("Arial", 12), bg="lightyellow").grid(row=7, column=0, sticky="w", pady=10)
time_combobox = ttk.Combobox(left_frame, values=["Select Time", "8:00 AM-9:00 AM", "10:00 AM-11:00 AM", "2:00 PM-3:00 PM", "4:00 PM-5:00 PM"], font=("Arial", 10), width=48)
time_combobox.set("Select Time")
time_combobox.grid(row=7, column=1, pady=10)

# Frame for Reservation List (Right side)
right_frame = tk.Frame(reservation_frame, padx=20, pady=20, bg="lightgreen")  # Set background color for right frame
right_frame.grid(row=0, column=1, padx=20, pady=20)

# Reservation List (Treeview)
tk.Label(right_frame, text="Reservations List", font=("Times", 20), bg="lightgreen").grid(row=0, column=0, columnspan=2, pady=10)

columns = ("Name", "Email", "Phone", "Class", "Instructor", "Time")
reservations_tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=20, style="Custom.Treeview")
reservations_tree.grid(row=1, column=0, columnspan=2, pady=15)

# Set up columns and headings
for col in columns:
    reservations_tree.heading(col, text=col)
    reservations_tree.column(col, width=123)

# Buttons (Add, Delete, Update)
buttons_frame = tk.Frame(right_frame, bg="lightgreen")
buttons_frame.grid(row=2, column=0, columnspan=2, pady=10)

# Add Button with larger font and size
add_button = ttk.Button(buttons_frame, text="Add Reservation", command=add_reservation, width=17, padding=10, style="MediumButton.TButton")
add_button.grid(row=0, column=0, padx=10)

# Delete Button with larger font and size
delete_button = ttk.Button(buttons_frame, text="Delete Reservation", command=delete_reservation, width=17, padding=10, style="MediumButton.TButton")
delete_button.grid(row=0, column=1, padx=10)

# Update Button with larger font and size
update_button = ttk.Button(buttons_frame, text="Update Reservation", command=update_reservation, width=17, padding=10, style="MediumButton.TButton")
update_button.grid(row=0, column=2, padx=10)

# Exit Button (Returns to login window)
exit_button = ttk.Button(buttons_frame, text="Exit", command=show_login_window, width=15, padding=10, style="MediumButton.TButton")
exit_button.grid(row=1, column=0, columnspan=3, pady=10)

# Show the login window initially
show_login_window()

# Start the GUI main loop
root.mainloop()