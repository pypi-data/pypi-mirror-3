'''A simple progress meter, using Tkinter for the widgets.

API example::

    @withprogress(300, color="green")
    def demo2():
        for i in range(300):
            # Do one (or a few) steps of processing, then...
            yield i
    
    try:
        demo2()
    except UserCancelled:
        print("Cancelled")
    else:
        print("Completed")
        
For more details, see the README, and object docstrings in this module.

Michael Lange <klappnase (at) freakmail (dot) de>
Thomas Kluyver <takowl (at) gmail (dot) com>
Based on Michael's ProgressMeter at:
http://tkinter.unpythonic.net/wiki/ProgressMeter
'''
from __future__ import division
import sys
from functools import wraps

try:
    from tkinter import Tk, Frame, Canvas, Button
except ImportError:
    from Tkinter import Tk, Frame, Canvas, Button

# Code below taken from six 1.1.0: http://pypi.python.org/pypi/six -------------
#Copyright (c) 2010-2011 Benjamin Peterson

#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#the Software, and to permit persons to whom the Software is furnished to do so,
#subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
if sys.version_info[0] >= 3:
    def reraise(tp, value, tb=None):
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value
else:
    exec("""def reraise(tp, value, tb=None):
    raise tp, value, tb
""")
# End of code from six ---------------------------------------------------------

class Meter(Frame):
    """
    The Meter class provides a simple progress bar widget for Tkinter.
    
    INITIALIZATION OPTIONS:
      The widget accepts all options of a Tkinter.Frame plus the following:

      fillcolor -- the color that is used to indicate the progress of the
                   corresponding process; default is "orchid1".
      value -- a float value between 0.0 and 1.0 (corresponding to 0% - 100%)
               that represents the current status of the process; values higher
               than 1.0 (lower than 0.0) are automagically set to 1.0 (0.0); default is 0.0 .
      text -- the text that is displayed inside the widget; if set to None the widget
              displays its value as percentage; if you don't want any text, use text="";
              default is None.
      font -- the font to use for the widget's text; the default is system specific.
      textcolor -- the color to use for the widget's text; default is "black".

    WIDGET METHODS:
    All methods of a Tkinter.Frame can be used; additionally there are two widget specific methods:

      get() -- returns a tuple of the form (value, text)
      set(value, text) -- updates the widget's value and the displayed text;
                          if value is omitted it defaults to 0.0 , text defaults to None .
    """
    def __init__(self, master, width=300, height=20, bg='white', fillcolor='orchid1',\
                 value=0.0, text=None, font=None, textcolor='black', *args, **kw):
        Frame.__init__(self, master, bg=bg, width=width, height=height, *args, **kw)
        self._value = value

        self._canv = Canvas(self, bg=self['bg'], width=self['width'], height=self['height'],\
                                    highlightthickness=0, relief='flat', bd=0)
        self._canv.pack(fill='both', expand=1)
        self._rect = self._canv.create_rectangle(0, 0, 0, self._canv.winfo_reqheight(), fill=fillcolor,\
                                                 width=0)
        self._text = self._canv.create_text(self._canv.winfo_reqwidth()/2, self._canv.winfo_reqheight()/2,\
                                            text='', fill=textcolor)
        if font:
            self._canv.itemconfigure(self._text, font=font)

        self.set(value, text)
        self.bind('<Configure>', self._update_coords)

    def _update_coords(self, event):
        '''Updates the position of the text and rectangle inside the canvas when the size of
        the widget gets changed.'''
        # looks like we have to call update_idletasks() twice to make sure
        # to get the results we expect
        self._canv.update_idletasks()
        self._canv.coords(self._text, self._canv.winfo_width()/2, self._canv.winfo_height()/2)
        self._canv.coords(self._rect, 0, 0, self._canv.winfo_width()*self._value, self._canv.winfo_height())
        self._canv.update_idletasks()

    def get(self):
        return self._value, self._canv.itemcget(self._text, 'text')

    def set(self, value=0.0, text=None):
        #make the value failsafe:
        if value < 0.0:
            value = 0.0
        elif value > 1.0:
            value = 1.0
        self._value = value
        if text == None:
            #if no text is specified use the default percentage string:
            text = str(int(round(100 * value))) + ' %'
        self._canv.coords(self._rect, 0, 0, self._canv.winfo_width()*value, self._canv.winfo_height())
        self._canv.itemconfigure(self._text, text=text)
        self._canv.update_idletasks()

class MeterWindow(Tk):
    def __init__(self, cancelbutton=False, barcolor="orchid1", **kwargs):
        Tk.__init__(self, **kwargs)
        self.meter = Meter(self, relief='ridge', fillcolor=barcolor, bd=3)
        self.meter.pack(fill='x')
        self.meter.set(0.0)
        if cancelbutton:
            self.cancel = Button(self, text="Cancel")
            self.cancel.pack()

class UserCancelled(Exception):
    "Exception raised when the user cancels processing with the cancel button."
    pass

def withprogress(upto=100, cancellable=True, title="Working...", color="orchid1"):
    """A decorator for a generator to run it with a progress bar.
    
    The generator should periodically yield a number between 0 and a maximum,
    given as the first argument here (default 100). On each yield, the progress
    bar will be updated. When the generator finishes, or raises an error, the
    progress bar is destroyed.
    
    If cancellable=True (the default), a cancel button will be presented to the
    user. If it's clicked, the generator will be stopped on the next yield, and
    a UserCancelled exception will be raised.
    """
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            # Create the GUI
            mw = MeterWindow(cancelbutton=cancellable, barcolor=color)
            mw.title(title)
            mw.meter.set(0.0)
            if cancellable:
                def _cancel():
                    wrapped._cancel = True
                mw.cancel.config(command=_cancel)
            
            gen = func(*args, **kwargs)
            def _step():
                if wrapped._cancel:
                    # User cancelled
                    mw.quit()
                    return
                try:
                    x = next(gen)
                except StopIteration:
                    # Nothing more to do
                    mw.quit()
                except:
                    wrapped._exc = sys.exc_info()
                    mw.quit()
                else:
                    mw.meter.set(x/upto)
                    mw.after(10, _step)
            
            mw.after(50, _step)
            mw.mainloop()
            
            # Did we finish normally?
            if wrapped._exc:
                reraise(wrapped._exc)
            if wrapped._cancel:
                raise UserCancelled

        wrapped._cancel = False
        wrapped._exc = None
        
        return wrapped
    return decorator

##-------------demo code--------------------------------------------##

if __name__ == '__main__':
    if len(sys.argv) < 2:
        @withprogress(300, color="green")
        def demo():
            for i in range(300):
                yield i
        
        try:
            demo()
        except UserCancelled:
            print("Cancelled")
        else:
            print("Completed")
    else:
        def _demostep(meter, value):
            meter.set(value)
            if value < 1.0:
                value = value + 0.005
                meter.after(50, lambda: _demostep(meter, value))
            else:
                meter.set(value, 'Demo successfully finished')

        def demo():
            root = MeterWindow(className='meter demo')
            root.meter.set(0.0, 'Starting demo...')
            root.after(1000, lambda: _demostep(root.meter, 0.0))
            root.mainloop()
        
        demo()
