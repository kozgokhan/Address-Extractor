import sqlite3
from tkinter import *
from tkinter.filedialog import askopenfilename
import ctypes

ctypes.windll.shcore.SetProcessDpiAwareness(1)

conn = sqlite3.connect(':memory:')
c = conn.cursor()
c.execute('''CREATE TABLE labels (name, type, address)''')


def get_address(filename):
    f = open(filename, 'r')
    f1 = f.readlines()
    begin_found = 0
    line = ''
    label_name = ''; description = ''; label_type = '';
    characteristic_len = len('/begin CHARACTERISTIC')
    measurement_len = len('/begin MEASUREMENT')
    
    for x in f1:
        begin_place = max(x.find('/begin MEASUREMENT'), x.find('/begin CHARACTERISTIC'))
        end_place = max(x.find('/end MEASUREMENT'), x.find('/end CHARACTERISTIC'))
        if (begin_place != -1):
            begin_found = 1
            
        if (begin_found == 1):
            line = line + x.rstrip('\n')
            
        if (end_place != -1): #end is found
            characteristic_found = line.find('/begin CHARACTERISTIC ')
            if (characteristic_found != -1):
                quote_pos = line.find('"')
                label_name = line[characteristic_found + characteristic_len : quote_pos].strip()
                desc_end_quote = quote_pos + line[quote_pos+1:-1].find('"')
                description = line[quote_pos+1:desc_end_quote+1]
                value_pos = line.find('VALUE ')
                label_address = str(line[value_pos+5:value_pos+16].strip())
                label_type = 'P'
                
            measurement_found = line.find('/begin MEASUREMENT ')
            if (measurement_found != -1):
                quote_pos = line.find('"')
                label_name = line[measurement_found + measurement_len : quote_pos].strip()
                desc_end_quote = quote_pos + line[quote_pos+1:-1].find('"')
                description = line[quote_pos+1:desc_end_quote+1]
                value_pos = line.find('ECU_ADDRESS ')
                label_address = str(line[value_pos+11:value_pos+22].strip())
                label_type = 'S'
    
            c.execute("INSERT INTO labels VALUES('"+ label_name +"','"+ label_type +"','"+ label_address +"')")
            begin_found = 0
            line = ""
            

def extract_address(address_list):
    f = open(address_list, 'r')
    f_o = open("label_output.txt","w")
    f1 = f.readlines()
    
    for x in f1:
        for row in c.execute("SELECT * FROM labels WHERE name='"+ x.rstrip('\n') +"'"):
            f_o.write(row[0] + ", " + row[2] + "\n")
    f.close()
    f_o.close()
    status_label.config(bg="green", text="The list has been created!")

a2l_name = ''
list_name = ''

def open_a2l_cmd():
    global a2l_name
    a2l_name = askopenfilename(filetypes =[("A2L files", "*.a2l")], title = "Choose an A2L file");
    get_address(a2l_name)
    a2l_select_st.config(fg="green", text="Selected")
    
def open_list_cmd():
    global list_name
    list_name = askopenfilename(filetypes =[("List", "*.txt")], title = "Choose Label List");
    extract_address(list_name)
    list_select_st.config(fg="green", text="Selected")
    
def exit_cmd():
    window.destroy()

window = Tk()
window.title("Address Finder")
window.geometry('500x200')
window.resizable(0, 0)

menubar = Menu(window)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Open .A2L", command=open_a2l_cmd)
filemenu.add_command(label="Open List", command=open_list_cmd)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=exit_cmd)
menubar.add_cascade(label="File", menu=filemenu)

a2l_label = Label(window, text="A2L File : ", anchor = W, justify=LEFT); a2l_label.place(x = 30, y = 20, width = 80, height = 30);
list_label = Label(window, text="Label List : ", anchor = W, justify=LEFT); list_label.place(x = 30, y = 70, width = 80, height = 30);
a2l_select_st = Label(window, text="Not Selected", anchor = W, justify=LEFT, fg="red"); a2l_select_st.place(x = 130, y = 20, width = 280, height = 30);
list_select_st = Label(window, text="Not Selected", anchor = W, justify=LEFT, fg="red"); list_select_st.place(x = 130, y = 70, width = 280, height = 30);

status_label = Label(window, text="Please select the files.", anchor = CENTER, justify=CENTER, fg="white", bg="red"); status_label.place(x = 30, y = 120, width = 440, height = 50);

window.config(menu=menubar)
window.mainloop()

