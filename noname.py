# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b3)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc


###########################################################################
## Class MyFrame1
###########################################################################

class MyFrame1(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition,
                          size=wx.Size(534, 447), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        bSizer3 = wx.BoxSizer(wx.VERTICAL)

        self.m_staticText1 = wx.StaticText(self, wx.ID_ANY, u"请输入原料", wx.DefaultPosition, wx.Size(500, -1),
                                           wx.ALIGN_CENTER_HORIZONTAL)
        self.m_staticText1.Wrap(-1)

        bSizer3.Add(self.m_staticText1, 0, wx.ALL, 5)

        self.m_filePicker2 = wx.FilePickerCtrl(self, wx.ID_ANY, wx.EmptyString, u"Select a file", u"*.*",
                                               wx.DefaultPosition, wx.Size(500, -1), wx.FLP_DEFAULT_STYLE)
        bSizer3.Add(self.m_filePicker2, 0, wx.ALL, 5)

        self.m_staticText2 = wx.StaticText(self, wx.ID_ANY, u"请输入产品", wx.DefaultPosition, wx.Size(500, -1),
                                           wx.ALIGN_CENTER_HORIZONTAL)
        self.m_staticText2.Wrap(-1)

        bSizer3.Add(self.m_staticText2, 0, wx.ALL, 5)

        self.m_filePicker3 = wx.FilePickerCtrl(self, wx.ID_ANY, wx.EmptyString, u"Select a file", u"*.*",
                                               wx.DefaultPosition, wx.Size(500, -1), wx.FLP_DEFAULT_STYLE)
        bSizer3.Add(self.m_filePicker3, 0, wx.ALL, 5)

        self.m_staticText3 = wx.StaticText(self, wx.ID_ANY, u"请输入禁接区", wx.DefaultPosition, wx.Size(500, -1),
                                           wx.ALIGN_CENTER_HORIZONTAL)
        self.m_staticText3.Wrap(-1)

        bSizer3.Add(self.m_staticText3, 0, wx.ALL, 5)

        self.m_filePicker4 = wx.FilePickerCtrl(self, wx.ID_ANY, wx.EmptyString, u"Select a file", u"*.*",
                                               wx.DefaultPosition, wx.Size(500, -1), wx.FLP_DEFAULT_STYLE)
        bSizer3.Add(self.m_filePicker4, 0, wx.ALL, 5)

        self.m_staticText4 = wx.StaticText(self, wx.ID_ANY, u"请输入参数", wx.DefaultPosition, wx.Size(500, -1),
                                           wx.ALIGN_CENTER_HORIZONTAL)
        self.m_staticText4.Wrap(-1)

        bSizer3.Add(self.m_staticText4, 0, wx.ALL, 5)

        self.m_textCtrl3 = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(500, -1), 0)
        bSizer3.Add(self.m_textCtrl3, 0, wx.ALL, 5)

        self.m_staticText5 = wx.StaticText(self, wx.ID_ANY, u"请选择方案", wx.DefaultPosition, wx.Size(500, -1),
                                           wx.ALIGN_CENTER_HORIZONTAL)
        self.m_staticText5.Wrap(-1)

        bSizer3.Add(self.m_staticText5, 0, wx.ALL, 5)

        self.m_checkBox1 = wx.CheckBox(self, wx.ID_ANY, u"贪婪解", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer3.Add(self.m_checkBox1, 0, wx.ALL, 5)

        self.m_checkBox2 = wx.CheckBox(self, wx.ID_ANY, u"成组批计算", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer3.Add(self.m_checkBox2, 0, wx.ALL, 5)

        self.m_button1 = wx.Button(self, wx.ID_ANY, u"经过代码编写", wx.DefaultPosition, wx.Size(500, -1), 0)
        bSizer3.Add(self.m_button1, 0, wx.ALL, 5)

        self.m_text_result = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(500, -1), 0)
        bSizer3.Add(self.m_text_result, 0, wx.ALL, 5)

        self.SetSizer(bSizer3)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.m_button1.Bind(wx.EVT_BUTTON, self.find_square)

    def __del__(self):
        pass

    # Virtual event handlers, override them in your derived class

    def find_square(self, event):
        event.Skip()


if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame1(None)
    frame.Show(True)
    # start the applications
    app.MainLoop()
