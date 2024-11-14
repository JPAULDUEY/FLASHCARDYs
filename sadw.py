import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# Database functions
def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS flashcard_sets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS flashcards (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        set_id INTEGER NOT NULL,
                        word TEXT NOT NULL,
                        definition TEXT NOT NULL,
                        FOREIGN KEY (set_id) REFERENCES flashcard_sets(id))''')
    conn.commit()

def add_set(conn, name):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO flashcard_sets (name) VALUES (?)', (name,))
    conn.commit()
    return cursor.lastrowid

def add_card(conn, set_id, word, definition):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO flashcards (set_id, word, definition) VALUES (?, ?, ?)',
                   (set_id, word, definition))
    conn.commit()
    return cursor.lastrowid

def get_sets(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM flashcard_sets')
    rows = cursor.fetchall()
    return {row[1]: row[0] for row in rows}

def get_cards(conn, set_id):
    cursor = conn.cursor()
    cursor.execute('SELECT word, definition FROM flashcards WHERE set_id = ?', (set_id,))
    return [(row[0], row[1]) for row in cursor.fetchall()]

# Main Application
class FlashcardApp:
    def __init__(self, root):
        self.conn = sqlite3.connect('flashcards.db')
        create_tables(self.conn)

        self.current_cards = []
        self.card_index = 0

        self.set_name_var = tk.StringVar()
        self.word_var = tk.StringVar()
        self.definition_var = tk.StringVar()

        # Set the root window background color
        root.configure(bg="#FFEBCC")  # Soft peach color for the main window

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        # Create tabs with custom frames and colors
        self.create_set_frame = self.create_set_tab()
        self.name_selections_frame = self.name_selections_tab()
        self.flashcard_frame = self.learn_mode_tab()

        self.populate_sets_combobox()

    # Create Set Tab (to create new sets)
    def create_set_tab(self):
        frame = tk.Frame(self.notebook, bg="#FFDD67")  # Light yellow background for the Create Set tab
        self.notebook.add(frame, text='Create Set')

        tk.Label(frame, text='Set Name:', background='#FFDD67', font=('Arial', 12, 'bold')).pack(padx=5, pady=5)
        tk.Entry(frame, textvariable=self.set_name_var, width=30).pack(padx=5, pady=5)

        tk.Button(frame, text='Save Set', command=self.create_set, bg='#FF7043', fg='white', activebackground='#FF5722').pack(padx=5, pady=10)

        return frame

    # Name Selections Tab (to select a set and add words/definitions)
    def name_selections_tab(self):
        frame = tk.Frame(self.notebook, bg="#FFB374")  # Warm light orange for the Name Selections tab
        self.notebook.add(frame, text="Name Selections")

        # Display selected set's name
        self.selected_set_name_label = tk.Label(frame, text="No set selected", font=('TkDefaultFont', 16), background='#FFB374')
        self.selected_set_name_label.pack(padx=10, pady=20)

        # Dropdown to select set
        tk.Label(frame, text="Select Set:", background='#FFB374').pack(padx=5, pady=5)
        self.sets_combobox = ttk.Combobox(frame, state='readonly')
        self.sets_combobox.pack(padx=5, pady=5)
        
        # Word and Definition input fields
        tk.Label(frame, text='Word:', background='#FFB374').pack(padx=5, pady=5)
        tk.Entry(frame, textvariable=self.word_var, width=30).pack(padx=5, pady=5)

        tk.Label(frame, text='Definition:', background='#FFB374').pack(padx=5, pady=5)
        tk.Entry(frame, textvariable=self.definition_var, width=30).pack(padx=5, pady=5)

        tk.Button(frame, text='Add Word', command=self.add_word, bg='#FF7043', fg='white', activebackground='#FF5722').pack(padx=5, pady=10)
        tk.Button(frame, text='Select Set', command=self.select_set, bg='#FF7043', fg='white', activebackground='#FF5722').pack(padx=5, pady=5)

        return frame

    # Learn Mode Tab (to review flashcards)
    def learn_mode_tab(self):
        frame = tk.Frame(self.notebook, bg="#FF7043")  # Warm orange for the Learn Mode tab
        self.notebook.add(frame, text='Learn Mode')

        # Word label with black color and Times New Roman font
        self.word_label = tk.Label(frame, text='', font=('Times New Roman', 32, 'bold'), background='#FF7043', foreground='black')
        self.word_label.pack(padx=5, pady=40)

        # Definition label with black color, Times New Roman font, and font size 20
        self.definition_label = tk.Label(frame, text='', font=('Times New Roman', 28), background='#FF7043', foreground='black')
        self.definition_label.pack(padx=5, pady=5)

        tk.Button(frame, text='Flip', command=self.flip_card, bg='#FF5722', fg='white', activebackground='#FF7043').pack(side='left', padx=5, pady=5)
        tk.Button(frame, text='Next', command=self.next_card, bg='#FF5722', fg='white', activebackground='#FF7043').pack(side='right', padx=5, pady=5)
        tk.Button(frame, text='Previous', command=self.prev_card, bg='#FF5722', fg='white', activebackground='#FF7043').pack(side='left', padx=5, pady=5)

        return frame

    # Populate Combobox with available sets
    def populate_sets_combobox(self):
        self.sets_combobox['values'] = tuple(get_sets(self.conn).keys())

    # Create a new set
    def create_set(self):
        set_name = self.set_name_var.get()
        if set_name:
            # Check if the set name already exists
            if set_name in get_sets(self.conn):
                messagebox.showinfo("Warning", "Name already exists. Please create another one.")
            else:
                add_set(self.conn, set_name)
                self.populate_sets_combobox()
                self.set_name_var.set('')  # Clear the entry field
                messagebox.showinfo("Success", f"Set '{set_name}' has been created successfully!")

    # Add word to a set
    def add_word(self):
        set_name = self.sets_combobox.get()
        word = self.word_var.get()
        definition = self.definition_var.get()

        if set_name and word and definition:
            sets = get_sets(self.conn)
            set_id = sets[set_name]
            add_card(self.conn, set_id, word, definition)
            self.word_var.set('')  # Clear word entry
            self.definition_var.set('')  # Clear definition entry

    # Select a set from combobox and display it in "Name Selections" tab
    def select_set(self):
        set_name = self.sets_combobox.get()
        if set_name:
            self.selected_set_name_label.config(text=f"Selected Set: {set_name}")
            # Optionally load the cards for the selected set (to view them in the learn tab)
            set_id = get_sets(self.conn)[set_name]
            self.current_cards = get_cards(self.conn, set_id)
            self.card_index = 0  # Start at the first card
            self.show_card()  # Display the first card

    # Learn flashcards
    def show_card(self):
        if self.current_cards:
            word, _ = self.current_cards[self.card_index]
            self.word_label.config(text=word)
            self.definition_label.config(text='')

    def flip_card(self):
        if self.current_cards:
            _, definition = self.current_cards[self.card_index]
            self.definition_label.config(text=definition)

    def next_card(self):
        if self.current_cards:
            self.card_index = min(self.card_index + 1, len(self.current_cards) - 1)
            self.show_card()

    def prev_card(self):
        if self.current_cards:
            self.card_index = max(self.card_index - 1, 0)
            self.show_card()

# Run the application
if __name__ == '__main__':
    root = tk.Tk()
    root.title('Flashcard App')
    root.geometry('500x400')

    app = FlashcardApp(root)
    root.mainloop()
