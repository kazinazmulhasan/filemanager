from tkinter import *
import os
import string
import re

class Application(Frame):
	def __init__(self, master=None):
		super().__init__(master)
		self.pack()
		self.panel_colors = ["gray80", "gray85"]
		self.clipboard = ""
		self.cal_sizes()
		self.load_images()
		self.add_menu()
		self.add_console()
		self.add_browse_panels(5)
		self.load_drives()
	
	def load_images(self):
		self.images = {}
		images = os.scandir("images/")
		for image in images:
			if image.is_file():
				self.images[image.name[0:-4]] = PhotoImage(file=image.path)
	
	def cal_sizes(self):
		self.width = self.winfo_screenwidth()
		self.height = {}
		height = self.winfo_screenheight() - 40
		self.height["menu"] = 50
		self.height["console"] = 50
		self.height["panel"] = height - self.height["menu"] - self.height["console"]
		print(self.width)
		print(self.height)
	
	def add_menu(self):
		self.menu = Frame(self, bd=0, height=self.height["menu"], width=self.width)
		self.menu.pack(side=TOP)
		self.menu_images = []
		self.add_menu_button("add_file", self.add_file_callback)
		self.add_menu_button("add_folder", self.add_folder_callback)
		self.add_menu_button("rename", self.rename_callback)
		self.add_menu_button("cut", self.cut_callback)
		self.add_menu_button("copy", self.copy_callback)
		self.add_menu_button("paste", self.paste_callback)
		self.add_menu_button("delete", self.delete_callback)
	
	def add_file_callback(self):
		self.console.delete(0, "end")
		self.console.insert(0, "touch ")
		self.console.focus()
	
	def add_folder_callback(self):
		self.console.delete(0, "end")
		self.console.insert(0, "mkdir ")
		self.console.focus()
	
	def rename_callback(self):
		pass
	
	def cut_callback(self):
		pass
	
	def copy_callback(self):
		pass
	
	def paste_callback(self):
		pass
	
	def delete_callback(self):
		print()
	
	def add_menu_button(self, name, callback):
		button = Button(self.menu, image=self.images[name], command=callback)
		button.pack(side=LEFT)
	
	def empty(self, panel):
		panel.delete(0, END)
	
	def hide(self, panel):
		panel.pack_forget()
	
	def add_browse_panels(self, count):
		self.panels = []
		width = int(self.width/(count*10))
		print(width)
		for i in range(count):
			panel = Listbox(self, bg=self.panel_colors[i%2], bd=1, height=self.height["panel"], width=width, selectmode=SINGLE, font=("Monaco", 12))
			panel.pid = i
			panel.addr = ""
			panel.bind("<Double-Button-1>", self.open)
			panel.bind("<Button-3>", self.clear_selection)
			panel.bind("<FocusIn>", self.set_curr_panel)
			panel.pack(side=LEFT)
			self.panels.append(panel)
		self.curr_pid = 0
	
	def open(self, event):
		widget = event.widget
		if widget.get(widget.curselection()[0])[-1:]=="/":
			# folder
			self.panel_load(widget.pid+1, widget.addr+widget.get(widget.curselection()[0]))
		else:
			os.chdir(widget.addr)
			os.startfile("\"%s\"" % widget.get(widget.curselection()[0]))
	
	def panel_load(self, pid, path):
		if pid < len(self.panels):
			panel = self.panels[pid]
			panel.addr = path
			for i in range(pid, len(self.panels)):
				self.empty(self.panels[i])
			for item in os.scandir(path):
				if item.is_dir():
					panel.insert(END, item.name+"/")
				else:
					panel.insert(END, item.name)
			panel.focus()
		else:
			pass
	
	def panel_refresh(self, panel):
		self.empty(panel)
		for item in os.scandir(panel.addr):
			if item.is_dir():
				panel.insert(END, item.name+"/")
			else:
				panel.insert(END, item.name)
	
	def clear_selection(self, event):
		event.widget.selection_clear(0, END)
	
	def set_curr_panel(self, event):
		if str(type(self.focus_get()))=="<class 'tkinter.Listbox'>":
			self.curr_pid = event.widget.pid
	
	def load_drives(self):
		self.panels[0].addr = ""
		letters = list(map(chr, range(65, 91)))
		for letter in letters:
			try:
				if os.path.exists("%s:" % letter):
					self.show_item(self.panels[0], letter+":/", "drive")
			except Exception as e:
				pass
	
	def show_item(self, panel, name, type):
		panel.insert(END, name)
	
	def add_console(self):
		frame = Frame(self, bd=0, height=self.height["console"], width=self.width)
		frame.pack(side=BOTTOM)
		self.console = Entry(frame, width=self.width, font=("Monaco", 12))
		self.console.bind("<Return>", self.exe_command)
		self.console.pack(side=LEFT)
	
	def exe_command(self, event):
		widget = event.widget
		text = widget.get()
		# print(text)
		text = re.split(r"\s+(?=(?=[^']*'[^']*')*[^']*$)", text)
		# print(text)
		if text[0]=="touch":
			# print("adding files")
			text.pop(0)
			self.add_file(self.panels[self.curr_pid], text)
		elif text[0]=="mkdir":
			# print("adding folders")
			self.add_folder(self.panels[self.curr_pid], text)
			
		widget.delete(0, "end")
	
	def add_file(self, parent, names):
		if parent.addr!="":
			for name in names:
				if not os.path.exists("%s/%s" % (parent.addr, name)):
					file = open("%s/%s" % (parent.addr, name), "w")
					file.close()
			self.panel_refresh(parent)

	def add_folder(self, parent, names):
		# print(parent.addr)
		# print(names)
		if parent.addr!="":
			for name in names:
				try:
					os.mkdir("%s/%s" % (parent.addr, name))
				except:
					pass
			self.panel_refresh(parent)

root = Tk()
root.wm_title("Oxiago File Manager")
root.state('zoomed')
app = Application(master=root)
app.mainloop()