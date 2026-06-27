import tkinter as tk
from tkinter import filedialog, messagebox

# Dictionary containing the opcode mappings
opcodes = {
    "NOP": "00",
    "LDA": "01",
    "LDB": "02",
    "LDX": "03",
    "LDY": "04",
    "LDT": "05",
    "LIA": "06",
    "LIB": "07",
    "LIX": "08",
    "LIY": "09",
    "LIT": "0A",
    "STA": "0B",
    "STB": "0C",
    "STX": "0D",
    "STY": "0E",
    "STK": "0F",
    "ADD": "10",
    "SUB": "11",
    "CMP": "12",
    "ADI": "13",
    "SUI": "14",
    "JMP": "70",
    "JPL": "71",
    "JPZ": "72",
    "JPE": "73",
    "JPG": "74",
    "JPC": "75",
    "JPY": "76",
    "AIJ": "77",
    "AIE": "78",
    "SYX": "20",
    "SXY": "21",
    "SYT": "22",
    "CAL": "30",
    "CAI": "32",
    "RET": "3100",
    "LVA": "40",
    "LVD": "41",
    "UPD": "4200",
    "RVA": "43",
    "RVD": "44",
    "LNR": "50",
    "LAR": "51",
    "LOR": "52",
    "LXR": "53"
}

# Symbol table to store labels and their memory addresses
symbol_table = {}

def insert_line_number(event):
    line_start = text_editor.index("insert linestart")
    line_text = text_editor.get(line_start, f"{line_start} lineend")
    if not line_text.strip().startswith("#") and not line_text.strip().startswith("$"):
        line_number = int(line_start.split('.')[0]) - 1
        text_editor.insert(line_start, f"${line_number:02X} ")
    text_editor.insert("insert", "\n")
    return "break"

def populate_symbol_table():
    text = text_editor.get("1.0", "end-1c")
    lines = text.split("\n")

    for idx, line in enumerate(lines):
        if line.strip() and not line.strip().startswith("#"):
            parts = line.split()
            if len(parts) >= 2:
                label = parts[0]
                mnemonic = parts[1]

                if mnemonic.endswith(":"):
                    label_name = mnemonic[:-1]
                    if label_name in symbol_table:
                        pass
                    symbol_table[label_name] = idx
    return True




def convert_to_machine_code():
    if not populate_symbol_table():
        return

    text = text_editor.get("1.0", "end-1c")
    lines = text.split("\n")
    machine_code = []

    for line in lines:
        if line.strip() and not line.strip().startswith("#"):
            parts = line.split()
            if len(parts) >= 2:
                label = parts[0]
                mnemonic = parts[1]

                if mnemonic.endswith(":"):
                    machine_code.append("0000")
                    if len(parts) == 3:
                        mnemonic = parts[2]
                    else:
                        continue
                else:
                    mnemonic = parts[1]

                if mnemonic in ["JMP", "JPC", "JPZ", "JPE", "JPG", "JPL", "CAL"]:
                    if len(parts) == 3:
                        target_label = parts[2]
                        if target_label in symbol_table:
                            target_address = symbol_table[target_label]
                            machine_code.append(f"{opcodes[mnemonic]}{target_address:02X}")
                        else:
                            messagebox.showerror("Error", f"Undefined label: {target_label}")
                            return
                    else:
                        messagebox.showerror("Error", f"{mnemonic} instruction requires a target label")
                        return
                elif mnemonic == "RET":
                    machine_code.append(opcodes[mnemonic])
                else:
                    opcode = opcodes.get(mnemonic)
                    if opcode:
                        if len(parts) == 3:
                            value = parts[2]
                            machine_code.append(f"{opcode}{value.upper()}")
                        else:
                            machine_code.append(opcode)
                    else:
                        messagebox.showerror("Error", f"Invalid mnemonic: {mnemonic}")
                        return

    result_box.delete("1.0", "end")
    result_box.insert("1.0", '\n'.join(machine_code))

def convert_lia_with_label():
    if not populate_symbol_table():
        return
    text = text_editor.get("1.0", "end-1c")
    lines = text.split("\n")
    new_lines = []

    for line in lines:
        parts = line.split(maxsplit=2)
        if len(parts) == 3 and parts[1] == "LIA":
            label = parts[2]
            if not label.isdigit() and label in symbol_table:  # Check if the operand is not a number
                address = symbol_table[label]
                lower_2_hex = address & 0xFF
                new_lines.append(f"{parts[0]} LIA {lower_2_hex:02X}")
            else:
                new_lines.append(line)  # Keep the line as it is if it's not a label
        else:
            new_lines.append(line)

    text_editor.delete("1.0", "end")
    text_editor.insert("1.0", "\n".join(new_lines))    

def convert_aij_with_label():
    if not populate_symbol_table():
        return

    text = text_editor.get("1.0", "end-1c")
    lines = text.split("\n")
    new_lines = []

    for line in lines:
        parts = line.split(maxsplit=2)
        if len(parts) == 3 and parts[1] == "AIJ":
            label = parts[2]
            if not label.isdigit() and label in symbol_table:
                address = symbol_table[label]
                upper_2_hex = (address >> 8) & 0xFF
                new_lines.append(f"{parts[0]} AIJ {upper_2_hex:02X}")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    text_editor.delete("1.0", "end")
    text_editor.insert("1.0", "\n".join(new_lines))


def convert_aie_with_label():
    if not populate_symbol_table():
        return

    text = text_editor.get("1.0", "end-1c")
    lines = text.split("\n")
    new_lines = []

    for line in lines:
        parts = line.split(maxsplit=2)
        if len(parts) == 3 and parts[1] == "AIE":
            label = parts[2]
            if not label.isdigit() and label in symbol_table:
                address = symbol_table[label]
                upper_2_hex = (address >> 8) & 0xFF
                new_lines.append(f"{parts[0]} AIE {upper_2_hex:02X}")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    text_editor.delete("1.0", "end")
    text_editor.insert("1.0", "\n".join(new_lines))

def convert_cai_with_label():
    if not populate_symbol_table():
        return

    text = text_editor.get("1.0", "end-1c")
    lines = text.split("\n")
    new_lines = []

    for line in lines:
        parts = line.split(maxsplit=2)
        if len(parts) == 3 and parts[1] == "CAI":
            label = parts[2]
            if not label.isdigit() and label in symbol_table:
                address = symbol_table[label]
                upper_2_hex = (address >> 8) & 0xFF
                new_lines.append(f"{parts[0]} CAI {upper_2_hex:02X}")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    text_editor.delete("1.0", "end")
    text_editor.insert("1.0", "\n".join(new_lines))





def convert_blc_command():
    text = text_editor.get("1.0", "end-1c")
    lines = text.split("\n")
    new_lines = []

    for line in lines:
        parts = line.split(maxsplit=3)
        if len(parts) == 4 and parts[1] == "BLC":
            line_number = parts[0]
            base_address = int(parts[2], 16)
            max_address = int(parts[3], 16)
            while base_address <= max_address:
                new_lines.append(f"{line_number} STA {base_address:02X}")
                # Increment the base address and line number for next instructions
                base_address += 1
                line_number = f"${int(line_number[1:], 16) + 1:02X}"
        else:
            new_lines.append(line)
    
    text_editor.delete("1.0", "end")
    text_editor.insert("1.0", "\n".join(new_lines))

def convert_high_level_code():
    text = text_editor.get("1.0", "end-1c")
    lines = text.split("\n")
    new_lines = []

    for line in lines:
        parts = line.split(maxsplit=2)  # Use maxsplit=2 to correctly handle the PNT command with spaces
        if len(parts) == 1 and parts[0].startswith('$'):
            new_lines.append(f"{parts[0]} NOP 00")
        elif len(parts) >= 2 and parts[1] == "PNT":
            if len(parts) != 3 or not (parts[2].startswith('"') and parts[2].endswith('"')):
                messagebox.showerror("Error", f"Invalid PNT syntax: {line}")
                return
            message = parts[2][1:-1]  # Extract the message inside quotes
            line_number = parts[0]  # Preserving the line number
            for char in message:
                if char == ' ':
                    new_lines.append(f"{line_number} LIT 20")  # Convert space to LIT 20
                else:
                    new_lines.append(f"{line_number} LIT {ord(char):02X}")
                # Increment the line number for the next instruction
                line_number = f"${int(line_number[1:], 16) + 1:02X}"
        else:
            new_lines.append(line)
    
    text_editor.delete("1.0", "end")
    text_editor.insert("1.0", "\n".join(new_lines))




def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Assembly files", "*.asm"), ("All files", "*.*")])
    if file_path:
        with open(file_path, "r") as file:
            content = file.read()
            text_editor.delete("1.0", "end")
            text_editor.insert("1.0", content)

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".asm", filetypes=[("Assembly files", "*.asm"), ("All files", "*.*")])
    if file_path:
        with open(file_path, "w") as file:
            content = text_editor.get("1.0", "end-1c")
            file.write(content)

def convert_back_to_mnemonics():
    machine_code = result_box.get("1.0", "end-1c")
    lines = machine_code.split("\n")
    mnemonics = []

    for line in lines:
        if line.strip():
            opcode = line[:2]
            value = line[2:]
            for mnemonic, opcode_value in opcodes.items():
                if opcode_value == opcode:
                    mnemonics.append(f"${lines.index(line):02X} {mnemonic} {value}")

    text_editor.delete("1.0", "end")
    text_editor.insert("1.0", '\n'.join(mnemonics))

def clear_text():
    text_editor.delete("1.0", "end")
    result_box.delete("1.0", "end")
    symbol_table.clear()

def highlight_syntax(event=None):
    text = text_editor.get("1.0", "end-1c")
    text_editor.tag_remove("mnemonic", "1.0", "end")
    text_editor.tag_remove("comment", "1.0", "end")

    lines = text.split("\n")
    for idx, line in enumerate(lines):
        start_idx = f"{idx + 1}.0"
        end_idx = f"{idx + 1}.end"

        if line.strip().startswith("#"):
            text_editor.tag_add("comment", start_idx, end_idx)
        else:
            for mnemonic in opcodes:
                if mnemonic in line:
                    start = line.index(mnemonic)
                    end = start + len(mnemonic)
                    text_editor.tag_add("mnemonic", f"{idx + 1}.{start}", f"{idx + 1}.{end}")

class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        self.delete("all")
        i = self.textwidget.index("@0,0")
        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            line_number = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=line_number, fill="gray")
            i = self.textwidget.index(f"{i}+1line")

class AutoCompleteEntry(tk.Entry):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.bind('<KeyRelease>', self.check_input)

    def check_input(self, event):
        text = self.get()
        suggestions = [mnemonic for mnemonic in opcodes if mnemonic.startswith(text)]
        if suggestions:
            self.show_suggestions(suggestions)
        else:
            self.hide_suggestions()

    def show_suggestions(self, suggestions):
        self.lb = tk.Listbox(self.parent)
        self.lb.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
        for suggestion in suggestions:
            self.lb.insert(tk.END, suggestion)
        self.lb.bind("<<ListboxSelect>>", self.fill_out)
        self.lb.bind("<Return>", self.fill_out)
        self.lb.bind("<Tab>", self.fill_out)

    def fill_out(self, event):
        selected = self.lb.get(tk.ACTIVE)
        self.delete(0, tk.END)
        self.insert(0, selected)
        self.lb.destroy()

    def hide_suggestions(self):
        if hasattr(self, 'lb'):
            self.lb.destroy()

# Create GUI
root = tk.Tk()
root.title("Assembly Code to Machine Code Converter")

# Text editor with line numbers
text_editor = tk.Text(root, height=40, width=80, undo=True, autoseparators=True, maxundo=-1)
text_line_numbers = TextLineNumbers(root, width=30)
text_line_numbers.attach(text_editor)

text_line_numbers.grid(row=0, column=0, sticky="ns")
text_editor.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
text_editor.bind("<Return>", insert_line_number)
text_editor.bind("<<Modified>>", highlight_syntax)

# Add tag configurations for syntax highlighting
text_editor.tag_configure("mnemonic", foreground="blue")
text_editor.tag_configure("comment", foreground="green")

# Convert LIA with label button
convert_lia_button = tk.Button(root, text="Convert LIA with Label", command=convert_lia_with_label)
convert_lia_button.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

# Convert AIE with label button
convert_aij_button = tk.Button(root, text="Convert AIE with Label", command=convert_aie_with_label)
convert_aij_button.grid(row=7, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

# Convert AIE with label button
convert_aij_button = tk.Button(root, text="Convert CAI with Label", command=convert_cai_with_label)
convert_aij_button.grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

# Convert AIJ with label button
convert_aij_button = tk.Button(root, text="Convert AIJ with Label", command=convert_aij_with_label)
convert_aij_button.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

convert_aij_button = tk.Button(root, text="Convert BLC", command=convert_blc_command)
convert_aij_button.grid(row=8, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

# Convert button
convert_button = tk.Button(root, text="Convert to Machine Code", command=convert_to_machine_code)
convert_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew", columnspan=2)

# Result box
result_box = tk.Text(root, height=25, width=40)
result_box.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

# Convert back button
convert_back_button = tk.Button(root, text="Convert Back to Mnemonics", command=convert_back_to_mnemonics)
convert_back_button.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

# Clear button
clear_button = tk.Button(root, text="Clear", command=clear_text)
clear_button.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

# Add new Convert High-Level Code button
convert_high_level_button = tk.Button(root, text="Convert High-Level Code", command= convert_high_level_code)
convert_high_level_button.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

# File menu
menu = tk.Menu(root)
root.config(menu=menu)
file_menu = tk.Menu(menu, tearoff=False)
menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)

# Make the columns stretchable
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=3)
root.columnconfigure(2, weight=2)

# Start the main loop
root.mainloop()
