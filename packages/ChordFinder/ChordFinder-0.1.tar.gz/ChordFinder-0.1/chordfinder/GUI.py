__author__ = 'Anthony'

import wx
import backend

class main_frame(wx.Frame): #Subclass Frame to make the main window
    def __init__(self,parent): #Overwrite parent constructor
        wx.Frame.__init__(self, parent, title="Chord Finder", style = wx.MINIMIZE_BOX, size = (200,200)) #Pass stuff to the parent constructor
        self.init_gui() #Do some GUI set up
        self.Center() #Center the window
        self.Show(True) #Show the window


    def init_gui(self):
        #Set up the main panel
        main_panel = wx.Panel(self)
        main_panel.SetBackgroundColour('#4f5049')

        #Title text
        title_text = wx.StaticText(main_panel,label= 'Chord Finder')
        title_text.SetForegroundColour((255,255,255))

        #Chord input TextCtrl
        self.chord_input = wx.TextCtrl(main_panel,id=100)
        self.chord_input.SetBackgroundColour((140,140,140))
        self.chord_input.SetFocus()
        box_focus = True

        #Chord output ListBox
        self.chord_output = wx.ListBox(main_panel, -1, size = (130,80))
        self.chord_output.SetBackgroundColour((140,140,140))


        #Vertical Sizer
        vert_sizer = wx.BoxSizer(wx.VERTICAL)


        #Add widgets to the vertical sizer
        vert_sizer.Add(title_text, 0, wx.CENTER | wx.TOP, 20)
        vert_sizer.Add(self.chord_output, 1, wx.CENTER | wx.ALL, 20)
        vert_sizer.Add(self.chord_input, 0, wx.CENTER | wx.ALL, 20)


        #Event bindings
        self.Bind(wx.EVT_TEXT, self.update_chords) #Update chords when the contents of the text box change
        self.Bind(wx.EVT_KEY_UP, self.on_key) #When a key is pressed


        #Set the sizer for the panel
        main_panel.SetSizer(vert_sizer)


    def on_key(self, event):
        """
        Called when a key is released
        """
        if event.GetKeyCode() == wx.WXK_RETURN and self.FindFocus() == self.chord_input: #If the input box has focus and the user presses enter
            self.chord_input.Clear()
        if event.GetKeyCode() == wx.WXK_ESCAPE: #Exit when escape is pressed
            self.Close()

    def update_chords(self, event):
        """
        Uses backend.find_chords to populate the listbox with chord names according to the notes in the input box
        """
        self.chord_output.Clear() #Clear the output box
        chords = backend.find_chords(self.chord_input.GetValue()) #Call the chord finder
        self.chord_output.Set(chords) #Display the results


app = wx.App(False) # Instantiate a WX application
main_frame_instance = main_frame(None) #Instantiate our main window
app.MainLoop() #Enter into main loop of app

