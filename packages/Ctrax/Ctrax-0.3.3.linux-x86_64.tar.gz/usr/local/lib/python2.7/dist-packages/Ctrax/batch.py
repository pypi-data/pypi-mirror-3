# batch.py
# KMB 11/06/2208

import os
import wx
from wx import xrc

import codedir
RSRC_FILE = os.path.join(codedir.codedir,'xrc','batch.xrc')

import movies
from params import params

class BatchWindow:
    def __init__( self, parent, directory, file_list=None ):
        self.file_list = []
        if file_list is not None: self.file_list.append( file_list )
        self.dir = directory
        self.executing = False

        self.ShowWindow( parent )

    def ShowWindow( self, parent ):
        rsrc = xrc.XmlResource( RSRC_FILE )
        self.frame = rsrc.LoadFrame( parent, "frame_Ctrax_batch" )

        # event bindings
        self.frame.Bind( wx.EVT_BUTTON, self.OnButtonAdd, id=xrc.XRCID("button_add") )
        self.frame.Bind( wx.EVT_BUTTON, self.OnButtonRemove, id=xrc.XRCID("button_remove") )
        self.frame.Bind( wx.EVT_BUTTON, self.OnButtonClose, id=xrc.XRCID("button_close") )
        self.frame.Bind( wx.EVT_CLOSE, self.OnButtonClose )

        # button handles
        self.add_button = xrc.XRCCTRL( self.frame, "button_add" )
        self.remove_button = xrc.XRCCTRL( self.frame, "button_remove" )
        self.execute_button = xrc.XRCCTRL( self.frame, "button_execute" )
        
        # textbox handle
        self.list_box = xrc.XRCCTRL( self.frame, "text_list" )
        self.list_box.Set( self.file_list )

        # autodetection options
        self.arena_choice = xrc.XRCCTRL(self.frame,"arena_choice")
        self.shape_choice = xrc.XRCCTRL(self.frame,"shape_choice")
        self.bg_model_choice = xrc.XRCCTRL(self.frame,"bg_model_choice")
        self.frame.Bind(wx.EVT_CHOICE,self.OnArenaChoice,id=xrc.XRCID("arena_choice"))
        self.frame.Bind(wx.EVT_CHOICE,self.OnShapeChoice,id=xrc.XRCID("shape_choice"))
        self.frame.Bind(wx.EVT_CHOICE,self.OnBgModelChoice,id=xrc.XRCID("bg_model_choice"))
        if params.batch_autodetect_arena == True:
            self.arena_choice.SetSelection(0)
        elif params.batch_autodetect_arena == False:
            self.arena_choice.SetSelection(1)
        else:
            self.arena_choice.SetSelection( 2 )
        if params.batch_autodetect_shape:
            self.shape_choice.SetSelection(0)
        else:
            self.bg_model_choice.SetSelection(1)
        if params.batch_autodetect_bg_model:
            self.bg_model_choice.SetSelection(0)
        else:
            self.bg_model_choice.SetSelection(1)

        self.sbfmf_checkbox = xrc.XRCCTRL( self.frame, "save_sbfmf" )

        self.frame.Show()
        self.is_showing = True

        self.EnableControls()

    def EnableControls( self ):
        """Enable or disable controls."""

        if not self.is_showing: return

        self.add_button.Enable( not self.executing )
        self.remove_button.Enable( not self.executing )
        self.execute_button.Enable( not self.executing )
        self.sbfmf_checkbox.Enable( not self.executing )
        self.arena_choice.Enable( not self.executing )
        self.shape_choice.Enable( not self.executing )
        self.bg_model_choice.Enable( not self.executing )

    def OnArenaChoice(self,evt):
        v = self.arena_choice.GetSelection()
        if v == 0:
            params.batch_autodetect_arena = True
        elif v == 1:
            params.batch_autodetect_arena = False
        else:
            params.batch_autodetect_arena = None

    def OnShapeChoice(self,evt):
        v = self.shape_choice.GetSelection()
        params.batch_autodetect_shape = (v == 0)
        
    def OnBgModelChoice(self,evt):
        v = self.bg_model_choice.GetSelection()
        params.batch_autodetect_bg_model = (v == 0)

    def OnButtonAdd( self, evt ):
        """Add button pressed. Select a movie to add to the batch."""
        try:
            movie = movies.Movie( self.dir, interactive=True, parentframe=self.frame, open_now=False )
        except ImportError:
            return

        self.dir = movie.dirname

        # check for duplicates
        add_flag = True
        for filename in self.file_list:
            if filename == movie.fullpath:
                wx.MessageBox( "File has already been added,\nnot duplicating",
                               "Duplicate", wx.ICON_WARNING )
                add_flag = False
                break
                
        if add_flag:
            self.file_list.append( movie.fullpath )
            self.list_box.Set( self.file_list )


    def OnButtonRemove( self, evt ):
        """Remove button pressed. Remove the currently selected movie from the queue."""
        for ii in reversed( range( len(self.file_list) ) ):
            if self.list_box.IsSelected( ii ):
                # don't remove currently executing job
                if not self.executing or ii != 0:
                    self.file_list.pop( ii )
        self.list_box.Set( self.file_list )


    def OnButtonClose( self, evt ):
        """Close button pressed. Close the batch window (batch processing may be ongoing)."""
        self.frame.Destroy()
        self.is_showing = False
