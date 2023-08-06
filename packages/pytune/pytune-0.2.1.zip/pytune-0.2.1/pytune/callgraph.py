# -*- coding:utf-8 -*-

import wx
import wx.lib.ogl as ogl
import panel

def get_fln_by_func(func):
        f, l, n = func
        f = f.rpartition('\\')[-1]
        return '%s(%s:%s)'%(n, f, l)

class MyEvtHandler(ogl.ShapeEvtHandler):
        def __init__(self):
                ogl.ShapeEvtHandler.__init__(self)
                self.callback = None
                #self.RightCallBack = None

        def OnLeftClick(self, *dontcare):
                shape = self.GetShape()
                self.callback(shape.func_id, shape.layer)

        def OnRightClick(self, *dontcare):
                can = self.GetShape().GetCanvas()
                self.GetShape().Delete()
                can.Refresh(False)
                print "%s\n" % self.GetShape()

class FuncShape(ogl.RectangleShape):
        def __init__(self, func_id, width = 0, height = 0, ):
                ogl.RectangleShape.__init__(self, width, height)
                self.func_id = func_id
                self.layer = 0
                self.fold = False


class MyCanvas(ogl.ShapeCanvas):
        def __init__(self, parent, initleft = 150, inittop = 50, 
                     width = 250, height = 100, max_width  = 10000, max_height = 10000,
                     rect_width = 150, rect_height = 50):
                ogl.ShapeCanvas.__init__(self, parent)
                
                self.width = width
                self.height = height
                self.initleft = initleft
                self.inittop = inittop
                self.rect_width = rect_width
                self.rect_height = rect_height
                self.SetScrollbars(20, 20, max_width/20, max_height/20)
                self.parent = parent
                self.SetBackgroundColour("LIGHT BLUE")
                self.diagram = ogl.Diagram()
                self.SetDiagram(self.diagram)
                self.diagram.SetCanvas(self)
                self.shapes = []
                self.lines = []
                self.total_func = 0
                self.layer_cnt = []

        def data_init(self, idls, iddt, cm):
                self.idls = idls
                self.iddt = iddt
                self.cm = cm
                self.total_func = len(idls)
                #self.fold_flag = [False]*self.total_func
                self.layer_cnt = [0]*self.total_func

                for i, func in enumerate(self.idls):
                        shape = FuncShape(i, self.rect_width, self.rect_height)
                        shape.SetCanvas(self)
                        shape.SetX(self.initleft)
                        shape.SetY(self.inittop)
                        shape.SetPen(wx.BLACK_PEN)
                        shape.SetBrush(wx.LIGHT_GREY_BRUSH)
                        for line in get_fln_by_func(func[0]).split('\n'):
                                shape.AddText(line)
                        #shape.SetShadowMode(ogl.SHADOW_RIGHT)
                        self.diagram.AddShape(shape)
                        #------------event-----------------
                        evthandler = MyEvtHandler()
                        evthandler.SetShape(shape)
                        evthandler.SetPreviousHandler(shape.GetEventHandler())
                        shape.SetEventHandler(evthandler)
                        evthandler.callback = self.fold_recursion
                        #------------event-----------------
                        self.shapes.append( shape )
                for i,ls in enumerate(self.cm):
                        tmp = []
                        for j in ls:
                                from_shape = self.shapes[i]
                                to_shape = self.shapes[j]
                                line = ogl.LineShape()
                                line.SetCanvas(self)
                                line.SetPen(wx.BLACK_PEN)
                                line.SetBrush(wx.BLACK_BRUSH)
                                line.AddArrow(ogl.ARROW_ARROW)
                                line.MakeLineControlPoints(2)
                                from_shape.AddLine(line, to_shape)
                                self.diagram.AddShape(line)
                                ##------------event-----------------
                                #evthandler = MyEvtHandler()
                                #evthandler.SetShape(line)
                                #evthandler.SetPreviousHandler(line.GetEventHandler())
                                #line.SetEventHandler(evthandler)
                                ##------------event-----------------
                                tmp.append(line)
                        self.lines.append(tmp)
                                

                indegree = [0]*self.total_func
                for i in cm:
                        for j in i:
                                indegree[j]+=1
                for i,j in enumerate(indegree):
                        if j == 0:
                                self.shapes[i].Show(True)
                                #self.fold_flag[i] = True
                                #list_1.append(i)
                self.Refresh()
                
        def fold_recursion(self, func_id, layer):
                if self.shapes[func_id].fold == True:
                        flag = False
                        self.shapes[func_id].fold = False
                else :
                        flag = True
                        self.shapes[func_id].fold = True
                list_1 = [func_id]
                list_2 = []
                while len(list_1)>0:
                        nextlayer = layer + 1
                        for func_id in list_1:
                                for i, func in enumerate(self.cm[func_id]):
                                        shape = self.shapes[func]
                                        if shape.layer == 0:
                                                shape.layer = nextlayer
                                        if shape.layer == nextlayer:
                                                shape.SetX(self.initleft + self.layer_cnt[nextlayer]*self.width)
                                                shape.SetY(self.inittop + nextlayer*self.height)
                                                if flag:
                                                        self.layer_cnt[nextlayer] += 1
                                                else :
                                                        self.layer_cnt[nextlayer] -= 1
                                                shape.Show(flag)
                                                if shape.fold == True:
                                                        list_2.append(func)
                                        if flag:
                                                self.shapes[func_id].AddLine(self.lines[func_id][i], shape)
                                        self.lines[func_id][i].Show(flag)
                        layer +=1
                        list_1 = list_2
                        list_2 = []
                self.Refresh()

        def fold_layer(self, func_id, layer):
                if self.shapes[func_id].fold == True:
                        flag = False
                        self.shapes[func_id].fold = False
                else :
                        flag = True
                        self.shapes[func_id].fold = True
                nextlayer = layer +1
                for i, func in enumerate(self.cm[func_id]):
                        shape = self.shapes[func]
                        if shape.layer == 0:
                                shape.layer = nextlayer
                        if shape.layer == nextlayer:
                                shape.SetX(self.initleft + self.layer_cnt[nextlayer]*self.width)
                                shape.SetY(self.inittop + nextlayer*self.height)
                                if flag:
                                        self.layer_cnt[nextlayer] += 1
                                else :
                                        self.layer_cnt[nextlayer] -= 1
                                shape.Show(flag)
                        if flag:
                                self.shapes[func_id].AddLine(self.lines[func_id][i], shape)
                        self.lines[func_id][i].Show(flag)
                self.Refresh()
                        

        def clear(self):
                self.diagram.DeleteAllShapes()
                self.shapes = []
                self.lines = []
                self.total_func = 0


class CallGraph(wx.Panel):
        def __init__(self, *a, **k):
                super(CallGraph, self).__init__(*a, **k)
                ogl.OGLInitialize()
                vbox = wx.BoxSizer(wx.VERTICAL)
                self.canvas = MyCanvas(self)

                vbox.Add(self.canvas, 1, wx.GROW)
                self.SetSizer(vbox)

        def init_data(self, stats):
                self.canvas.clear()
                idls = stats.id_list
                iddt = stats.id_dict
                cm = stats.call_map
                self.canvas.data_init(idls, iddt, cm)


                #sp = ogl.RectangleShape(85, 50)#, 105, 60, wx.BLACK_PEN, wx.LIGHT_GREY_BRUSH, "Function1" )

                #list_1 = []
                #list_2 = []
                #flag = [True]*len(idls)
                #for i,j in enumerate(indegree):
                        #if j == 0:
                                #list_1.append(i)
                #layer = 0
                #cnt = 0
                #for i in list_1:
                        #self.canvas.add_shape(i, ogl.RectangleShape(150, 50), initleft + cnt*w, inittop + layer*h, 
                                              #wx.BLACK_PEN, wx.LIGHT_GREY_BRUSH, str(idls[i][0]) )
                        #flag[i]=False
                        #cnt+=1
                #layer += 1
                #while len(list_1)>0:
                        #cnt = 0
                        #for i in list_1:
                                #for pnt in cm[i]:
                                        #if flag[pnt] == True:
                                                #self.canvas.add_shape(pnt, ogl.RectangleShape(150, 50), initleft + cnt*w, inittop + layer*h, 
                                                                      #wx.BLACK_PEN, wx.LIGHT_GREY_BRUSH, get_fln_by_func(idls[pnt][0]) )
                                                #flag[pnt]=False
                                                #list_2.append(pnt)
                                                #cnt +=1
                                        #self.canvas.add_line(i,pnt)
                        #list_1 = list_2
                        #list_2 = []
                        #layer +=1

                #self.canvas.render()


#def CallGraph(parent, *a, **k):
        #obj = wx.Panel(parent, *a, **k)

        #return obj