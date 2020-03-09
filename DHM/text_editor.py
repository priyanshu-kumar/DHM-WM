try:
    import tkinter as tk

except:
    import Tkinter as tk

try:
    import tkMessageBox as pop_up
    import tkFileDialog as tkFileDialog
except:
    import tkinter.tkMessageBox as pop_up
    import tkinter.tkFileDialog as tkFileDialog

import time
import ntpath

EMPTY_TITLE_ERROR_MESSAGE_SAVE = "Please write the name of the file you want to save in the given field."
EMPTY_TITLE_ERROR_MESSAGE_OPEN = "Please write the name of the file you want to open in the given field."
FILE_NOT_FOUND_ERROR_MESSAGE = "No file with the given title was found, remember that this text editor can only read files in its directory."
SAVING_SUCCESS_MESSAGE = "Your text is now stored in the {filename} file"
SIGNATURE_TXT_NOT_FOUND_MESSAGE = "Please be sure that the file you want to open exists and that it is in the same folder of this editor."


def _open(filelocation):
    if filelocation !="empty":
            root.filelocation =filelocation

    if file_title.get() !="":
        if not ".txt" in file_title.get():
            root.filelocation = file_title.get() + ".txt"
        else:
            root.filelocation =file_title.get()
    elif filelocation =="empty":
        root.filelocation = tkFileDialog.askopenfilename(initialdir="/", title="Open Text File",
                                                         filetypes=(("Text", ".txt"), ("All Files", "*.*")))
        print(root.filelocation)



    try:
        with open(root.filelocation) as f:
            head, tail = ntpath.split(root.filelocation)
            root.title(tail)
            main_text.delete("1.0",tk.END)
            main_text.insert(tk.INSERT, f.read(), "a")

    except IOError:
        pop_up.showerror("File not found.",FILE_NOT_FOUND_ERROR_MESSAGE)

def save():
    if file_title.get() !="":
        if not ".txt" in file_title.get():
            filename = file_title.get() + ".txt"
        else:
            filename = file_title.get()
    elif root.filelocation is not None:
       filename = root.filelocation
    else:
        pop_up.showerror("No title.",EMPTY_TITLE_ERROR_MESSAGE_SAVE)
        return 1


    try:
        with open(filename,"w+") as f:
            f.write(main_text.get(1.0,tk.END))
            pop_up.showinfo("File saved succesfully.", SAVING_SUCCESS_MESSAGE.format(filename=filename))
    except Exception as err:
        pop_up.showinfo("File Not saved.", err)

def add_date():
    full_date = time.localtime()
    day = str(full_date.tm_mday)
    month = str(full_date.tm_mon)
    year = str(full_date.tm_year)
    date = "\n"+day+'/'+month+'/'+year
    main_text.insert(tk.INSERT, date, "a")

def add_signature():
    try:
        with open("signature.txt") as f:
            main_text.insert(tk.INSERT, "\n"+f.read(), "a")
    except IOError:
        MESSAGE = SIGNATURE_TXT_NOT_FOUND_MESSAGE
        pop_up.showerror("\"signature.txt\" not found.",MESSAGE)

def openEditor(root1,file=None):
    global fileLocation, main_text, root, file_title
    root=root1
    # root = tk.Tk()
    root.title("Text Editor")
    menubar = tk.Menu(root)
    menubar.add_command(label="Open", command=lambda: _open("empty"))
    menubar.add_command(label="Save", command=save)
    menubar.add_command(label="Add signature",command=add_signature)
    menubar.add_command(label="Add date",command=add_date)


    root.config(menu=menubar)

    top = tk.Frame(root)
    temp = tk.Label(root,text="Title:")
    temp.pack(in_ = top,side=tk.LEFT)

    file_title = tk.Entry(root)
    file_title.pack(in_ = top,side=tk.RIGHT)

    top.pack()

    main_text = tk.Text(root)
    main_text.pack()
    if file!="empty":
        _open(file)
    tk.mainloop()

