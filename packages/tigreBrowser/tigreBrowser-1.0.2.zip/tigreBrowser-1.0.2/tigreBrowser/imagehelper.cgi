#! /usr/bin/env python

import cgi
import cgitb; cgitb.enable()
import os
import sys
from tigreBrowser.browser_utils import *
from tigreBrowser.database import *
from string import Template

try:
    from Tkinter import *
    from tkFileDialog import askopenfilename
    from tkMessageBox import *
except ImportError, e:
    pass

try:
    from ConfigParser import RawConfigParser
except:
    from configparser import RawConfigParser

CONFIG_FILE = 'tigreBrowser.cfg'
DATABASE_FILE = None

# TODO Python 2.5 and 3.x compatibility

def read_config_file(config_file):
    config = RawConfigParser()
    if not config.read(config_file):
        if not config.read('../' + config_file):
            print_error_message("Config file '%s' not found" % config_file, True)
    try:
        database_file = config.get('tigreBrowser', 'database').strip('\'\"')
    except (Exception,):
        e = sys.exc_info()[1] # Python >3.0 compatibility
        print_error_message(e, True)
    return database_file

# TODO better tables
def print_list_as_table(listing):
    print("<table>")
    for elem in listing:
        print("<tr><td>%s</td></tr>" % elem)
    print("</table>")

def print_dataset_row(db, form, odd, dataset_id, name, species, source, platform, description, save_location, figure_filename):
    print("<tr %s>" % """class="odd" """ if odd else "")
    print("<td>%s</td>" % name)
    print("<td>")
    print_input(form, 'dataset_filename_' + str(dataset_id), figure_filename, size='100')
    print("</td>")
    print("</tr>")

def print_figure_row(db, form, odd, figure_id, filename, name, desc, priority):
    experiment_ids = db.get_figure_experiments(figure_id)
    print("<tr %s>" % """class="odd" """ if odd else "")
    dataset_names = []
    experiment_names = []
    regulators = []
    target_genes = []
    for experiment_id in experiment_ids:
        dataset_names.append(db.get_experiment_dataset_name(experiment_id))
        experiment_names.append(db.get_experiment_name(experiment_id))
        regulators.append(db.get_experiment_regulator_name(experiment_id))
        target_genes.append(', '.join(db.get_experiment_target_genes(experiment_id)))

    print("<td>")
    print_list_as_table(dataset_names)
    print("</td>")
    print("<td>")
    print_list_as_table(experiment_names)
    print("</td>")
    print("<td>")
    print_list_as_table(regulators)
    print("</td>")
    print("<td>")
    print_list_as_table(target_genes)
    print("</td>")

    print("<td>")
    print_input(form, 'figure_filename_' + str(figure_id), filename, size='100')
    print("</td>")
    print("<td>")
    print_input(form, 'figure_name_' + str(figure_id), name, size='20')
    print("</td>")
    print("<td>")
    print_input(form, 'figure_desc_' + str(figure_id), desc, size='20')
    print("</td>")
    print("<td>")
    print_input(form, 'figure_priority_' + str(figure_id), priority, size='2')
    print("</td>")
    print("</tr>")

def print_form(db, form, experiment_figuredata, dataset_annotations):
    location = os.getenv("SCRIPT_URI") or ""
    print('<form action="' + location + '" method="get">')

    print("<fieldset>")
    print("<legend>Dataset figures</legend>")
    print("<table>")
    print("<tr>")
    print("<th>Dataset name</th>")
    print("<th>Figure</th>")
    print("</tr>")
    for (row, annotation) in enumerate(dataset_annotations):
        print_dataset_row(db, form, row % 2 == 0, *annotation)
    print("</table>")
    print("</fieldset>")

    print("<fieldset>")
    print("<legend>Experiment figures</legend>")
    print("<table>")
    print("<tr>")
    print("<th>Dataset name</th>")
    print("<th>Experiment name</th>")
    print("<th>Regulator</th>")
    print("<th>Targets</th>")
    print("<th>Figure filename</th>")
    print("<th>Figure name</th>")
    print("<th>Figure description</th>")
    print("<th>Figure priority</th>")
    print("</tr>")
    for (row, figure) in enumerate(experiment_figuredata):
        print_figure_row(db, form, row % 2 == 0, *figure)
    print("</table>")
    print("</fieldset>")
    print("""<p class="submit"><input type="submit" value="Save"/></p>""")
    print("""</form>""")

def update_dataset_figures_in_db(db, form):
    if not form.keys():
        return
    figures = {}
    for key in form.keys():
        strings = key.strip().split('_')
        if strings[0] != 'dataset':
            continue
        dataset_id = int(strings[-1])
        if strings[1] != 'filename':
            print("<strong>Error</strong>")
        figures[dataset_id] = form.getvalue(key)

    for (dataset_id, filename) in figures.items():
        db.c.execute("""UPDATE expression_dataset_annotation
                        SET figure_filename = ?
                        WHERE  dataset_id = ?""", (filename, dataset_id))
        db.conn.commit()

def update_experiment_figures_in_db(db, form):
    if not form.keys():
        return
    figures = {}
    for key in form.keys():
        strings = key.strip().split('_')
        if strings[0] != 'figure':
            continue
        figure_id = int(strings[-1])
        figures.setdefault(figure_id, [None, None, None, None]) # filename, name, desc, priority
        type = strings[1]
        if type == 'filename':
            figures[figure_id][0] = form.getvalue(key)
        elif type == 'name':
            figures[figure_id][1] = form.getvalue(key)
        elif type == 'desc':
            figures[figure_id][2] = form.getvalue(key)
        elif type == 'priority':
            figures[figure_id][3] = int(form.getvalue(key))
        else:
            print("<strong>Error</strong>")
            return

    annotations = []
    for (k, v) in figures.items():
        annotations.append([k] + v)

    try:
        for annotation in annotations:
            db.c.execute("""REPLACE INTO figure_annotation
                            VALUES (?, ?, ?, ?, ?)""", annotation)
            db.conn.commit()
    except sqlite3.OperationalError, error:
        print_error_message(error)
    print("<strong>Database updated!</strong>")

def print_error_message(message, print_header=False):
    if print_header:
        print_headers("Imagehelper")
    print("<strong>Error: %s</strong>" % message)
    print_footer()
    sys.exit(1)

def get_database_file_error(database_file):
    if not os.path.isfile(database_file):
        return "Database file not found"
    if not os.access(database_file, os.W_OK):
        return "Database file must have write permissions"
    dirname = os.path.dirname(database_file)
    if not os.access(dirname, os.W_OK):
        return "The directory containing the database file must have write permissions"

def ensure_database_is_writable(database_file):
    if not os.path.isfile(database_file):
        print_error_message("Database file '%s' not found" % os.path.join(os.getcwd(), database_file), True)
    if not os.access(database_file, os.W_OK):
        print_error_message("Database file '%s' must have write permissions" % os.path.join(os.getcwd(), database_file), True)
    dirname = os.path.dirname(database_file) or os.getcwd()
    if not os.access(dirname, os.W_OK):
        print_error_message("The directory '%s' containing the database file must have write permissions" % os.getcwd(), True)

def web_main():
    form = cgi.FieldStorage()
    script_url = os.getenv("SCRIPT_URL")
    query_string = os.getenv("QUERY_STRING")

    database_file = read_config_file(CONFIG_FILE)
    ensure_database_is_writable(database_file)

    try:
        db = Database(database_file)
        experiment_figuredata = db.get_figure_annotations()
        dataset_annotations = db.get_dataset_annotations()
    except sqlite3.DatabaseError, error:
        print_error_message(error, True)

    print_headers("Imagehelper")

    print_form(db, form, experiment_figuredata, dataset_annotations)

    update_dataset_figures_in_db(db, form)
    update_experiment_figures_in_db(db, form)

    print_footer()

##########
# Tk

try:
    class Imagehelper(Frame):
        def __init__(self, master=None):
            Frame.__init__(self, master)
            self.pack()
            self.create_widgets()

        def create_widgets(self):
            self.title = Label(self, text="Imagehelper")
            self.title.pack({"side": "top"})

            self.dataset_frame = Frame(self)
            self.dataset_frame.pack()

            self.experiment_frame = Frame(self)
            self.experiment_frame.pack()

            self.button_frame = Frame(self)
            self.button_frame.pack()

            self.open = Button(self.button_frame, text="Open database file", command=self.open_db)
            self.open.pack({"side": "left"})

            self.save = Button(self.button_frame, text="Save changes", command=self.save_db, state=DISABLED)
            self.save.pack({"side": "right"})

        def open_db(self):
            database_file = askopenfilename(filetypes=[("SQLite database files", "*.sqlite"), ("All files", "*")])
            if not database_file:
                return
            message = get_database_file_error(database_file)
            if message:
                showerror("Error!", message)
                return

            try:
                self.db = Database(database_file)
                experiment_figuredata = self.db.get_figure_annotations()
                dataset_annotations = self.db.get_dataset_annotations()
            except sqlite3.DatabaseError, error:
                showerror("Error!", error)

            self.create_form(database_file, experiment_figuredata, dataset_annotations)
            self.open.config(state=DISABLED)

        def save_db(self):
            self.save_dataset_figures()
            self.save_experiment_figures()

        def save_experiment_figures(self):
            print("Saving experiment figures")
            for (figure_id, string_var) in self.figure_filename_entries.items():
                filename = string_var.get()
                name = self.figure_name_entries[figure_id].get()
                desc = self.figure_desc_entries[figure_id].get()
                try:
                    priority = self.figure_priority_entries[figure_id].get()
                except ValueError:
                    priority = None
                annotation = [figure_id, filename, name, desc, priority]
                self.db.c.execute("""REPLACE INTO figure_annotation
                                     VALUES (?, ?, ?, ?, ?)""", annotation)
                self.db.conn.commit()

        def save_dataset_figures(self):
            print("Saving dataset figures")
            for (dataset_id, string_var) in self.dataset_entries.items():
                filename = string_var.get()
                self.db.c.execute("""UPDATE expression_dataset_annotation
                                     SET figure_filename = ?
                                     WHERE dataset_id = ?""", (filename, dataset_id))
                self.db.conn.commit()

        # TODO grid
        def create_dataset_figure_widgets(self, frame, row, dataset_id, name, species, source, platform, description, save_location, figure_filename):
            label = Label(frame, text=name)
            label.grid(row=row, column=0)

            v = StringVar()
            v.set(figure_filename)
            self.dataset_entries[dataset_id] = v
            entry = Entry(frame, width=100, textvariable=v)
            entry.grid(row=row, column=1)

        def create_experiment_figure_widgets(self, frame, row, figure_id, filename, name, desc, priority):
            experiment_ids = self.db.get_figure_experiments(figure_id)
            dataset_names = []
            experiment_names = []
            regulators = []
            target_genes = []
            for experiment_id in experiment_ids:
                dataset_names.append(self.db.get_experiment_dataset_name(experiment_id))
                experiment_names.append(self.db.get_experiment_name(experiment_id))
                regulators.append(self.db.get_experiment_regulator_name(experiment_id))
                target_genes.append(', '.join(self.db.get_experiment_target_genes(experiment_id)))

            if not name:
                name = ""
            if not desc:
                desc = ""
            if not priority:
                priority = ""

            r = self.add_list_to_grid(dataset_names, frame, row, 0)
            r = max(r, self.add_list_to_grid(experiment_names, frame, row, 1))
            r = max(r, self.add_list_to_grid(regulators, frame, row, 2))
            r = max(r, self.add_list_to_grid(target_genes, frame, row, 3))

            filename_v = StringVar()
            filename_v.set(filename)
            self.figure_filename_entries[figure_id] = filename_v
            filename_entry = Entry(frame, width=80, textvariable=filename_v)
            filename_entry.grid(row=row, column=4, rowspan=r - row)

            name_v = StringVar()
            name_v.set(name)
            self.figure_name_entries[figure_id] = name_v
            name_entry = Entry(frame, width=15, textvariable=name_v)
            name_entry.grid(row=row, column=5, rowspan=r - row)

            desc_v = StringVar()
            desc_v.set(desc)
            self.figure_desc_entries[figure_id] = desc_v
            desc_entry = Entry(frame, width=15, textvariable=desc_v)
            desc_entry.grid(row=row, column=6, rowspan=r - row)

            priority_v = IntVar()
            priority_v.set(desc)
            self.figure_priority_entries[figure_id] = priority_v
            priority_entry = Entry(frame, width=3, textvariable=priority_v)
            priority_entry.grid(row=row, column=7, rowspan=r - row)

            return r

        # TODO headers: colors, etc.
        # TODO row borders, bg, etc.

        def add_list_to_grid(self, listing, frame, row, column):
            for elem in listing:
                label = Label(frame, text=elem)
                label.grid(row=row, column=column)
                row += 1
            return row

        def create_dataset_frame(self, dataset_annotations):
            dataset_label = Label(self.dataset_frame, text="Dataset figures")
            dataset_label.pack()

            dataset_f = Frame(self.dataset_frame)
            dataset_f.pack()

            name_h = Label(dataset_f, text="Dataset name")
            name_h.grid(row=0, column=0)

            figure_h = Label(dataset_f, text="Figure")
            figure_h.grid(row=0, column=1)

            self.dataset_entries = {}
            for (row, annotation) in enumerate(dataset_annotations):
                self.create_dataset_figure_widgets(dataset_f, row + 1, *annotation)

        def create_experiment_frame(self, experiment_figuredata):
            experiment_label = Label(self.experiment_frame, text="Experiment figures")
            experiment_label.pack()

            frame = Frame(self.experiment_frame)
            frame.pack()

            l = Label(frame, text="Dataset name")
            l.grid(row=0, column=0)
            l = Label(frame, text="Experiment name")
            l.grid(row=0, column=1)
            l = Label(frame, text="Regulator")
            l.grid(row=0, column=2)
            l = Label(frame, text="Targets")
            l.grid(row=0, column=3)
            l = Label(frame, text="Figure filename")
            l.grid(row=0, column=4)
            l = Label(frame, text="Figure name")
            l.grid(row=0, column=5)
            l = Label(frame, text="Figure description")
            l.grid(row=0, column=6)
            l = Label(frame, text="Figure priority")
            l.grid(row=0, column=7)

            self.figure_filename_entries = {}
            self.figure_name_entries = {}
            self.figure_desc_entries = {}
            self.figure_priority_entries = {}

            row = 1
            for figure in experiment_figuredata:
                row = self.create_experiment_figure_widgets(frame, row, *figure) + 1

        def create_form(self, database_file, experiment_figuredata, dataset_annotations):
            filename_label = Label(self, text="Database file:" + database_file)
            filename_label.pack({"side": "bottom"})

            self.create_dataset_frame(dataset_annotations)
            self.create_experiment_frame(experiment_figuredata)

            self.save.config(state=NORMAL)
except NameError:
    pass

if os.getenv("REMOTE_ADDR"):
    web_main()
else:
    root = Tk()
    app = Imagehelper(master=root)
    app.mainloop()
    root.destroy

