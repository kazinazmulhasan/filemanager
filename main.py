from tkinter import *
import os
import string
import re
from shutil import copyfile

panel_count = 8

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
		self.add_browse_panels(panel_count)
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
		# self.add_menu_button("rename", self.rename_callback)
		# self.add_menu_button("cut", self.cut_callback)
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
	
	def get_selected_item(self):
		panel = self.panels[self.curr_pid]
		name = panel.get(panel.curselection()[0])
		if name[-1:] == "/":
			name = name[:-1]
		return name
	
	def rename_callback(self):
		self.console.delete(0, "end")
		self.console.insert(0, "rename '%s' '%s' " % (self.panels[self.curr_pid].addr, self.get_selected_item()))
		self.console.focus()
	
	def cut_callback(self):
		pass
	
	def copy_callback(self):
		self.clipboard = [self.panels[self.curr_pid].addr, self.get_selected_item()]
	
	def paste_callback(self):
		if self.clipboard != "":
			panel = self.panels[self.curr_pid]
			dst = panel.addr+self.clipboard[1]
			copyfile(self.clipboard[0]+self.clipboard[1], dst)
			self.panel_refresh(panel)
			
	
	def delete_callback(self):
		panel = self.panels[self.curr_pid]
		name = self.get_selected_item()
		if name[-1:]=="/":
			name = name[:-1]
			os.rmdir("%s%s" % (panel.addr, name))
		else:
			os.remove("%s%s" % (panel.addr, name))
		self.panel_refresh(panel)
	
	def add_menu_button(self, name, callback):
		button = Button(self.menu, image=self.images[name], command=callback)
		button.pack(side=LEFT)
	
	def empty(self, panel):
		panel.delete(0, END)
	
	def hide(self, panel):
		panel.pack_forget()
	
	def add_browse_panels(self, count):
		self.panels = []
		self.panel_width = int(self.width/(count*10))
		for i in range(count):
			self.add_panel(i, "")
		self.curr_pid = 0
	
	def add_panel(self, pid, path):
		panel = Listbox(self, bg=self.panel_colors[pid%2], bd=1, height=self.height["panel"], width=self.panel_width, selectmode=SINGLE, font=("Monaco", 12))
		panel.pid = pid
		panel.addr = path
		panel.bind("<Double-Button-1>", self.open)
		panel.bind("<Button-3>", self.clear_selection)
		panel.bind("<FocusIn>", self.set_curr_panel)
		panel.bind("<Escape>", self.panel_close)
		panel.pack(side=LEFT)
		self.panels.append(panel)
	
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
			for i in range(pid, len(self.panels)):
				self.empty(self.panels[i])
				panel.addr = path
		else:
			for panel in self.panels[0:len(self.panels)-panel_count+1]:
				self.hide(panel)
			self.add_panel(pid, path)
			print("new panel added")
		for item in os.scandir(path):
			if item.is_dir():
				panel.insert(END, item.name+"/")
			else:
				panel.insert(END, item.name)
		panel.focus()
	
	def panel_refresh(self, panel):
		if panel.addr == "":
			return
		self.empty(panel)
		for item in os.scandir(panel.addr):
			if item.is_dir():
				panel.insert(END, item.name+"/")
			else:
				panel.insert(END, item.name)
	
	def panel_close(self, event):
		# print(dir(event))
		# return
		widget = event.widget
		if widget.pid == len(self.panels)-1 and widget.pid >= panel_count:
			print("closing panel")
			self.empty(widget)
			for panel in self.panels:
				panel.pack_forget()
			widget.destroy()
			self.panels.pop()
			for panel in self.panels[(panel_count*-1)-1:]:
				panel.pack(side=LEFT)
			self.panels[0].delete(self.panels[0].count, END)
	
	def clear_selection(self, event):
		event.widget.selection_clear(0, END)
	
	def set_curr_panel(self, event):
		if str(type(self.focus_get()))=="<class 'tkinter.Listbox'>":
			self.curr_pid = event.widget.pid
	
	def load_drives(self):
		self.panels[0].addr = ""
		count = 0
		letters = list(map(chr, range(65, 91)))
		for letter in letters:
			try:
				if os.path.exists("%s:" % letter):
					self.show_item(self.panels[0], letter+":/", "drive")
					count += 1
			except Exception as e:
				pass
		self.panels[0].count = count
	
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
			text.pop(0)
			self.add_folder(self.panels[self.curr_pid], text)
		elif text[0]=="rename":
			try:
				self.rename(text[1], text[2], text[3])
			except Exception as e:
				print(e)
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
	
	def rename(self, cwd, old_name, new_name):
		# os.chdir(cwd)
		# os.replace(old_name, new_name, cwd, cwd)
		os.system("ren %s%s %s%s" % (cwd[:-1], old_name[1:], cwd[:-1], new_name[1:]) )
		self.panel_refresh(self.panels[self.curr_pid])

root = Tk()
root.wm_title("Oxiago File Manager")
root.state('zoomed')
app = Application(master=root)
app.mainloop()