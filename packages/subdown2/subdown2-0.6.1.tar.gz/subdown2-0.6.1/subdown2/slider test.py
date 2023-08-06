import math,time
from Tkinter import *

class Application(Frame):

	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.grid()
		self.createWidgets()
		
		
	def createWidgets(self):
	
		self.Slider = Scale(self, from_=0, to_=100, resolution=.1, orient=HORIZONTAL)
		self.Slider.grid(row=0,column=0)
		
		self.sliderbutton = Button(self, text='Set to 50', command=self.sliderevent)
		self.sliderbutton.grid(row=2,column=1)
		
		
	def sliderevent(self):
	
		#self.value = float(self.Slider.get())
		self.Slider.set(25.0)
		self.Slider.set(50.0)
		
		#print 'Slider Value = %f' %self.value
		
		
App = Application()
App.mainloop()
