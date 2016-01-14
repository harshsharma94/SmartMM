#!/usr/bin/env python

from filemanager import *
import gettext
import subprocess
import darkmode
import movieicon

class RenameFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.label_1 = wx.TextCtrl(self, wx.ID_ANY,"Movie Name")
        self.button_1 = wx.Button(self, wx.ID_ANY, _("Set"))
        self.Bind(wx.EVT_BUTTON,self.do_rename,self.button_1)
        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def do_rename(self,event):
        index = MainFrame.my_selection
        list = MainFrame.customized_movies_list.GetItems()
        mov_id = mov_to_id(list[index])
        new_name = self.label_1.GetValue()
        manager = SQLHandler()
        manager.handle.execute("""
                              UPDATE videoinfo
                              SET videoname='%s'
                              WHERE id=%d
                              """ % (new_name,mov_id))
        manager.handle.commit()
        manager.close()
        MainFrame.customized_movies_list.SetString(index,new_name)
        Rename.Show(0)

    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle(_("Rename"))
        self.SetSize((200, 70))
        self.label_1.SetFont(wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 1, ""))
        self.button_1.SetMinSize((60, 30))
        self.button_1.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.label_1, 0, wx.EXPAND, 0)
        sizer_2.Add(self.button_1, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        self.Layout()
        # end wxGlade

class ReviewFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.label_1 = wx.StaticText(self, wx.ID_ANY, _("Movie NAme"))
        self.label_2 = wx.StaticText(self, wx.ID_ANY, _("-reviewer naem"))
        self.label_3 = wx.StaticText(self, wx.ID_ANY, _("Reviews"))
        self.panel_1 = wx.Panel(self, wx.ID_ANY)
        self.label_4 = wx.TextCtrl(self.panel_1, wx.ID_ANY, _("fdsvsdvfsdvsdv"), style=wx.TE_READONLY|wx.TE_MULTILINE)
        self.button_1 = wx.Button(self, wx.ID_ANY, _("Back"))
        self.Bind(wx.EVT_BUTTON,self.go_back,self.button_1)

        self.__set_properties()
        self.__do_layout()
    # end wxGlade

    def go_back(self,event):
        MainFrame.Show(1)
        Reviews.Show(0)

    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle(_("Read Review"))
        self.SetSize((900, 700))
        self.label_1.SetMinSize((211, 47))
        self.label_1.SetFont(wx.Font(25, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 1, ""))
        self.label_2.SetMinSize((190, 29))
        self.label_2.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.label_3.SetMinSize((81, 24))
        self.label_3.SetFont(wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.label_4.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.panel_1.SetMinSize((800, 550))
        self.button_1.SetMinSize((90, 40))
        self.button_1.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
    # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.label_1, 0, wx.EXPAND, 0)
        sizer_2.Add(self.label_2, 0, 0, 0)
        sizer_2.Add(self.label_3, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_3.Add(self.label_4, 1, wx.EXPAND, 0)
        self.panel_1.SetSizer(sizer_3)
        sizer_2.Add(self.panel_1, 1, wx.EXPAND, 0)
        sizer_2.Add(self.button_1, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        self.Layout()
    # end wxGlade

class MainFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        #   Initialize
        kwds["style"] = wx.DEFAULT_FRAME_STYLE & (~wx.RESIZE_BORDER)
        self.frame = wx.Frame.__init__(self, *args, **kwds)
        self.panel = wx.Panel(self.frame)
        self.defaultBackgroundColour = self.GetBackgroundColour()
        # self.SetBackgroundColour(wx.BLACK)
        self.PhotoMaxSize = 150
        #Menubar
        self.setup_menubar()

        #Movies List
        self.my_selection = 0
        self.setup_movlist()

        #Movie Details
        self.setup_movdetails()

        #Setup Properties
        self.__set_properties()
        self.__do_layout()
        # Autoload
        mov_names = get_mov_names()
        if len(mov_names) != 0:
            map(self.add_movie,mov_names)
        else:
            print "First Load"
            first_load()

    def setup_movdetails(self):
        self.mov_name = wx.StaticText(self, wx.ID_ANY, _("(My Movie \nName) Year Genre"), style=wx.ALIGN_CENTER)
        ######  Image Handling
        img = wx.EmptyImage(self.PhotoMaxSize,self.PhotoMaxSize)
        self.mov_poster = wx.StaticBitmap(self, wx.ID_ANY,
                                         wx.BitmapFromImage(img))
        self.set_scale_img(movieicon.getmovies_iconImage())
        ## Excellent Link for doing above : http://www.blog.pythonlibrary.org/2008/05/23/wxpython-embedding-an-image-in-your-title-bar/
        ######
        self.mov_plot = wx.TextCtrl(self, wx.ID_ANY, _(""), style=wx.TE_READONLY|wx.TE_MULTILINE)
        self.imdb_rating = wx.StaticText(self, wx.ID_ANY, _("IMDb Rating"))
        self.imdb_rating_val = wx.StaticText(self, wx.ID_ANY, _("-/10"))
        self.starcast = wx.StaticText(self, wx.ID_ANY, _("Starcast"))
        self.starcast_val = wx.TextCtrl(self, wx.ID_ANY, _(""),style=wx.TE_READONLY)
        self.rt_rating = wx.StaticText(self, wx.ID_ANY, _(" Rotten Tomatoes\n       Rating"))
        self.rt_rating_val = wx.StaticText(self, wx.ID_ANY, _("-/10"))
        self.director = wx.StaticText(self, wx.ID_ANY, _("Director"))
        self.director_val = wx.TextCtrl(self, wx.ID_ANY, _(""),style=wx.TE_READONLY)
        self.imdb_votes = wx.StaticText(self, wx.ID_ANY, _("Vote Count"))
        self.imdb_votes_val = wx.StaticText(self, wx.ID_ANY, _(""))
        self.producer = wx.StaticText(self, wx.ID_ANY, _("Producer"))
        self.producer_val = wx.TextCtrl(self, wx.ID_ANY, _(""),style=wx.TE_READONLY)
        self.review_title = wx.StaticText(self, wx.ID_ANY, _("Reviews"), style=wx.ALIGN_CENTER_HORIZONTAL)
        self.reviews_list = wx.ListBox(self, wx.ID_ANY, style=wx.LB_MULTIPLE)
        self.Bind(wx.EVT_LISTBOX_DCLICK,self.double_click_review_list,self.reviews_list)

    def setup_movlist(self):
        self.title_label = wx.StaticText(self, wx.ID_ANY, _("Video Listing"))
        self.customized_movies_list = wx.ListBox(self, wx.ID_ANY, style=wx.LB_MULTIPLE)
        self.Bind(wx.EVT_LISTBOX,self.single_click_mov_list,self.customized_movies_list)
        self.Bind(wx.EVT_LISTBOX_DCLICK,self.double_click_mov_list,self.customized_movies_list)
        self.customized_movies_list.Bind(wx.EVT_RIGHT_UP,self.right_click_mov_list)

    def setup_menubar(self):
        self.Menu = wx.MenuBar()
        self.file = wx.Menu()
        self.folder = wx.MenuItem(self.file, wx.ID_ANY, _("Add Folder"), "", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU,self.on_browse_folder,self.folder)
        self.file.AppendItem(self.folder)
        self.files = wx.MenuItem(self.file, wx.ID_ANY, _("Add Files"), "", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU,self.on_browse_file,self.files)
        self.file.AppendItem(self.files)
        self.sync = wx.MenuItem(self.file, wx.ID_ANY, _("Synchronize"), "", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU,self.synchronize,self.sync)
        self.file.AppendItem(self.sync)
        self.reset = wx.MenuItem(self.file, wx.ID_ANY, _("Reset"), "", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU,self.reset_mov_list,self.reset)
        self.file.AppendItem(self.reset)
        self.Menu.Append(self.file, _("File"))
        self.about = wx.Menu()
        self.themetoggle = wx.MenuItem(self.about, wx.ID_ANY, _("Toggle Theme"), "", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU,self.toggle_themes,self.themetoggle)
        self.about.AppendItem(self.themetoggle)
        self.exit = wx.MenuItem(self.about, wx.ID_EXIT, _("Exit"), "", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU,self.close_me,self.exit)
        self.about.AppendItem(self.exit)
        self.Menu.Append(self.about, _("Extras"))
        self.SetMenuBar(self.Menu)

    def reset_mov_list(self,event):
        SQLHandler().resetdb()
        self.clean_details()
        self.customized_movies_list.Clear()

    def toggle_themes(self,event):
        darkmode.darkMode(MainFrame,self.defaultBackgroundColour)
        darkmode.darkMode(Reviews,self.defaultBackgroundColour)
        darkmode.darkMode(Rename,self.defaultBackgroundColour)

    def add_movie(self,mov_name):
        self.customized_movies_list.Insert(mov_name,self.customized_movies_list.GetCount())

    def add_review(self,review_info):
        self.reviews_list.Insert("%s\t%s" % review_info,self.reviews_list.GetCount())

    def single_click_mov_list(self, event):
        index = event.GetSelection()
        list = self.customized_movies_list.GetItems()
        self.my_selection = index
        req_id = mov_to_id(list[index])
        try:
            mov_dict = prep_mov_details_dict(req_id)
            self.mov_name.SetLabel("%s\n%s" % (mov_dict["name"],mov_dict["genres"]))
            self.imdb_rating_val.SetLabel(str(mov_dict["imdb_rating"]))
            self.imdb_votes_val.SetLabel(str(mov_dict["votes"]))
            self.rt_rating_val.SetLabel(str(mov_dict["rt_rating"]))
            self.set_scale_img(blob_to_wximage(mov_dict["img"]))
            self.mov_plot.Clear()
            self.mov_plot.WriteText(str(mov_dict["plot"]))
            self.director_val.Clear()
            self.director_val.WriteText(str(mov_dict["directors"]))
            self.producer_val.Clear()
            self.producer_val.WriteText(str(mov_dict["producers"]))
            self.starcast_val.Clear()
            self.starcast_val.WriteText(str(mov_dict["cast"]))
            reviewers = mov_dict["reviewers"]
            review_urls = mov_dict["review_urls"]
            reviews_info = zip(reviewers,review_urls)
            self.reviews_list.Clear()
            map(self.add_review,reviews_info)
        except Exception as e:
            print e
            self.clean_details()

    def double_click_mov_list(self, event):
        index = event.GetSelection()
        list = self.customized_movies_list.GetItems()
        path = mov_to_path(list[index])
        subprocess.Popen(["vlc",path],shell=False)

    def right_click_mov_list(self,event):
        """
        Create and show a Context Menu
        """
        # only do this part the first time so the events are only bound once
        if not hasattr(self, "delete_item"):
            self.delete_item = wx.NewId()
            self.rename = wx.NewId()
            self.Bind(wx.EVT_MENU, self.delete_mov_item, id=self.delete_item)
            self.Bind(wx.EVT_MENU, self.rename_text, id=self.rename)

        # build the menu
        menu = wx.Menu()
        menu.Append(self.delete_item, "Delete Item")
        menu.Append(self.rename, "Rename")

        # show the popup menu
        self.PopupMenu(menu)
        menu.Destroy()

    def rename_text(self,event):
        Rename.Show()

    def delete_mov_item(self,event):
        index = self.my_selection
        list = self.customized_movies_list.GetItems()
        print len(list)
        req_id = mov_to_id(list[index])
        print req_id
        self.clean_details()
        SQLHandler().delete_record(req_id)
        self.customized_movies_list.Clear()
        map(self.add_movie,get_mov_names())
        self.my_selection = -1

    def double_click_review_list(self,event):
        selected_rev_index = event.GetSelection()
        mov_id = mov_to_id(self.customized_movies_list.GetItems()[self.my_selection])
        mov_dict = prep_mov_details_dict(mov_id)
        mov_name = mov_dict["name"]
        reviewer_name = mov_dict["reviewers"][selected_rev_index]
        review = mov_dict["reviews"][selected_rev_index]
        Reviews.label_1.SetLabel(mov_name)
        Reviews.label_2.SetLabel(reviewer_name)
        Reviews.label_4.Clear()
        Reviews.label_4.WriteText(str(review))
        Reviews.Show(1)
        self.Show(0)

    def on_browse_folder(self, event):
        """
        Browse for folder
        """
        dialog = wx.DirDialog(None, "Choose a Directory",
                               style = wx.DD_DEFAULT_STYLE)
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
            if os.path.isdir(path):
                add_folder(path)
                map(self.add_movie,list(set(get_mov_names()) - set(self.customized_movies_list.GetItems())))
            else:
                print "Incorrect Input"
        dialog.Destroy()

    def on_browse_file(self, event):
        """
        Browse for file
        """
        wildcard = "Select Folder (*.*)|*.*"
        dialog = wx.FileDialog(None, "Choose a File",
                               wildcard=wildcard,
                               style=wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
            if os.path.isfile(path):
                add_file(path)
                map(self.add_movie,list(set(get_mov_names()) - set(self.customized_movies_list.GetItems())))
            else:
                print "Incorrect Input"
        dialog.Destroy()

    def synchronize(self, event):
        internet_sync()

    def close_me(self, event):
        self.Close(True)

    def clean_details(self):
        self.mov_name.SetLabel("Information Missing")
        self.imdb_rating_val.SetLabel("")
        self.imdb_votes_val.SetLabel("")
        self.rt_rating_val.SetLabel("")
        self.mov_plot.Clear()
        self.director_val.Clear()
        self.producer_val.Clear()
        self.starcast_val.Clear()
        self.reviews_list.Clear()
        self.set_scale_img(movieicon.getmovies_iconImage())

    def set_scale_img(self,img):
        W = img.GetWidth()
        H = img.GetHeight()
        if W > H:
            NewW = self.PhotoMaxSize
            NewH = self.PhotoMaxSize * H / W
        else:
            NewH = self.PhotoMaxSize
            NewW = self.PhotoMaxSize * W / H
        img = img.Scale(NewW,NewH)
        self.mov_poster.SetBitmap(wx.BitmapFromImage(img))
        self.panel.Refresh()

    def __set_properties(self):
        # begin wxGlade: MainFrame.__set_properties
        self.SetTitle(_("Movie Management System"))
        self.SetSize((841, 496))
        self.title_label.SetMinSize((114, 30))
        self.reviews_list.SetMinSize((wx.FULL_REPAINT_ON_RESIZE,40))
        self.title_label.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.mov_name.SetMinSize((400, 50))
        self.mov_name.SetFont(wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.imdb_rating.SetFont(wx.Font(13, wx.DECORATIVE, wx.SLANT, wx.NORMAL, 0, ""))
        self.starcast.SetFont(wx.Font(13, wx.DECORATIVE, wx.SLANT, wx.NORMAL, 0, ""))
        self.rt_rating.SetFont(wx.Font(13, wx.DECORATIVE, wx.SLANT, wx.NORMAL, 0, ""))
        self.director.SetFont(wx.Font(13, wx.DECORATIVE, wx.SLANT, wx.NORMAL, 0, ""))
        self.imdb_votes.SetFont(wx.Font(13, wx.DECORATIVE, wx.SLANT, wx.NORMAL, 0, ""))
        self.producer.SetFont(wx.Font(13, wx.DECORATIVE, wx.SLANT, wx.NORMAL, 0, ""))
        self.review_title.SetMinSize((80, 10))
        self.review_title.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.reviews_list.SetSelection(0)
        self.starcast_val.SetMinSize((140,30))
        self.director_val.SetMinSize((140,30))
        self.producer_val.SetMinSize((140,30))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MainFrame.__do_layout
        listing_details_split = wx.BoxSizer(wx.HORIZONTAL)
        title_below_split = wx.BoxSizer(wx.VERTICAL)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1 = wx.GridSizer(3, 4, 0, 0)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        title_list_split = wx.BoxSizer(wx.VERTICAL)
        title_list_split.Add(self.title_label, 0, wx.ALIGN_CENTER, 0)
        title_list_split.Add(self.customized_movies_list, 10, wx.EXPAND, 1)
        listing_details_split.Add(title_list_split, 1, wx.EXPAND, 0)
        title_below_split.Add(self.mov_name, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_2.Add(self.mov_poster, 1, wx.EXPAND|wx.LEFT, 50)
        sizer_2.Add(self.mov_plot, 2, wx.EXPAND, 0)
        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        grid_sizer_1.Add(self.imdb_rating, 0, wx.ALIGN_CENTER, 0)
        grid_sizer_1.Add(self.imdb_rating_val, 0, wx.ALIGN_CENTER, 0)
        grid_sizer_1.Add(self.starcast, 0, wx.ALIGN_CENTER, 0)
        grid_sizer_1.Add(self.starcast_val, 0, wx.ALIGN_CENTER, 0)
        grid_sizer_1.Add(self.rt_rating, 0, wx.ALIGN_CENTER, 0)
        grid_sizer_1.Add(self.rt_rating_val, 0, wx.ALIGN_CENTER, 0)
        grid_sizer_1.Add(self.director, 0, wx.ALIGN_CENTER, 0)
        grid_sizer_1.Add(self.director_val, 0, wx.ALIGN_CENTER, 0)
        grid_sizer_1.Add(self.imdb_votes, 0, wx.ALIGN_CENTER, 0)
        grid_sizer_1.Add(self.imdb_votes_val, 0, wx.ALIGN_LEFT|wx.LEFT|wx.UP, 15)
        grid_sizer_1.Add(self.producer, 0, wx.ALIGN_CENTER, 0)
        grid_sizer_1.Add(self.producer_val, 0, wx.ALIGN_CENTER, 0)
        sizer_1.Add(grid_sizer_1, 1, 0, 0)
        sizer_3.Add(self.review_title, 3, wx.EXPAND, 0)
        sizer_3.Add(self.reviews_list, 10, wx.EXPAND, 1)
        sizer_1.Add(sizer_3, 1, 0, 0)
        title_below_split.Add(sizer_1, 1, wx.EXPAND, 0)
        listing_details_split.Add(title_below_split, 3, wx.EXPAND, 0)
        self.SetSizer(listing_details_split)
        self.Layout()
        # end wxGlade

if __name__ == "__main__":
    print "Starting"
    gettext.install("Movie Management System")
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    Reviews = ReviewFrame(None, wx.ID_ANY, "")
    MainFrame = MainFrame(None, wx.ID_ANY, "")
    Rename = RenameFrame(None, wx.ID_ANY, "")
    app.SetTopWindow(MainFrame)
    MainFrame.Show()
    app.MainLoop()
