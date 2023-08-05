__author__ = 'dgraziotin'
"""
This module holds the GUI for representing a Package. Currently it is used only for showing
relevant information about a Package. It will also be used for creating a Package.
"""
import datadeck.settings as settings
import base
import wx.xrc


class CreatePackageGUI(object):
    def __init__(self, xml):
        self.m_xml = xml
        self.m_frame = xml.LoadFrame(None, 'DataDeck')
        self.m_panel =  wx.xrc.XRCCTRL(self.m_frame, 'create_panel')
        name = wx.xrc.XRCCTRL(self.m_frame, 'name_text')
        name.SetValue("cacca")



