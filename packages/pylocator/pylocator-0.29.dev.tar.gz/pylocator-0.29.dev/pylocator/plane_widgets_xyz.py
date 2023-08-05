import gtk
import vtk

from events import EventHandler, UndoRegistry, Viewer
from marker_window_interactor import MarkerWindowInteractor
from image_reader import widgets

import numpy as np
from scipy import array, zeros

from shared import shared

def move_pw_to_point(pw, xyz):

    n = pw.GetNormal()
    o = pw.GetOrigin()
    pxyz = [0,0,0]
    vtk.vtkPlane.ProjectPoint(xyz, o, n, pxyz)
    transform = vtk.vtkTransform()
    transform.Translate(xyz[0]-pxyz[0], xyz[1]-pxyz[1], xyz[2]-pxyz[2])
    p1 = transform.TransformPoint(pw.GetPoint1())
    p2 = transform.TransformPoint(pw.GetPoint2())
    o = transform.TransformPoint(o)

    pw.SetOrigin(o)                
    pw.SetPoint1(p1)
    pw.SetPoint2(p2)
    pw.UpdatePlacement()


class PlaneWidgetsXYZ(MarkerWindowInteractor):
    """
    CLASS: PlaneWidgetsXYZ

    DESCR: Upper left frame of window. Contains 3 rotatable image plane
    widgets, and possibly a .vtk mesh.
    """
        
    def __init__(self, imageData=None):
        MarkerWindowInteractor.__init__(self)

        if shared.debug: print "PlaneWidgetsXYZ.__init__()"

        self.vtksurface = None

        self.interactButtons = (1,2,3)
        self.sharedPicker = vtk.vtkCellPicker()
        #self.sharedPicker.SetTolerance(0.005)
        self.SetPicker(self.sharedPicker)
        
        self.pwX = vtk.vtkImagePlaneWidget()
        self.pwY = vtk.vtkImagePlaneWidget()
        self.pwZ = vtk.vtkImagePlaneWidget()

        
        self.textActors = {}
        self.boxes = {}

        self.axes_labels = []

        self.set_image_data(imageData)
        self.Render()

        self.vtk_translation = zeros(3, 'd')
        self.vtk_rotation = zeros(3, 'd')

    def translate_vtk(self, axis, value):
        if (axis == 'x'): ax = 0
        elif (axis == 'y'): ax = 1
        elif (axis == 'z'): ax = 2
        self.vtk_translation[ax]=value
        self.scaleTransform.Identity()
        self.scaleTransform.RotateX(self.vtk_rotation[0])
        self.scaleTransform.RotateY(self.vtk_rotation[1])
        self.scaleTransform.RotateZ(self.vtk_rotation[2])
        self.scaleTransform.Translate(self.vtk_translation[0],self.vtk_translation[1],self.vtk_translation[2])
        self.Render()
        
    def rotate_vtk(self, axis, value):
        if (axis == 'x'): ax = 0
        elif (axis == 'y'): ax = 1
        elif (axis == 'z'): ax = 2
        self.vtk_rotation[ax]=value
        self.scaleTransform.Identity()
        self.scaleTransform.RotateX(self.vtk_rotation[0])
        self.scaleTransform.RotateY(self.vtk_rotation[1])
        self.scaleTransform.RotateZ(self.vtk_rotation[2])
        self.scaleTransform.Translate(self.vtk_translation[0],self.vtk_translation[1],self.vtk_translation[2])
        self.Render()

    def set_image_data(self, imageData):
        if shared.debug: print "PlaneWidgetsXYZ.set_image_data()!!"
        if imageData is None: return 
        self.imageData = imageData
        extent = self.imageData.GetBounds()#Extent()
        if shared.debug: print "***Extent:", extent
        frac = 0.3

        self._plane_widget_boilerplate(
            self.pwX, key='x', color=(1,0,0),
            index=frac*(extent[1]-extent[0]),
            orientation=0)

        self._plane_widget_boilerplate(
            self.pwY, key='y', color=(1,1,0),
            index=frac*(extent[3]-extent[2]),
            orientation=1)
        self.pwY.SetLookupTable(self.pwX.GetLookupTable())

        self._plane_widget_boilerplate(
            self.pwZ, key='z', color=(0,0,1),
            index=frac*(extent[5]-extent[4]),
            orientation=2)
        self.pwZ.SetLookupTable(self.pwX.GetLookupTable())
        
        self.pwX.SetResliceInterpolateToCubic()
        self.pwY.SetResliceInterpolateToCubic()
        self.pwZ.SetResliceInterpolateToCubic()
        for pw in [self.pwX,self.pwY,self.pwZ]:
            move_pw_to_point(pw,self.imageData.GetCenter())
        #self.pwZ.SetResliceInterpolateToNearestNeighbour()
        self.camera = self.renderer.GetActiveCamera()

        #center = self.imageData.GetCenter()
        #spacing = self.imageData.GetSpacing()
        #bounds = np.array(self.imageData.GetBounds())
        #if shared.debug: print "***center,spacing,bounds", center,spacing,bounds
        #pos = center[0], center[1], center[2] - max((bounds[1::2]-bounds[0::2]))*2
        #fpu = center, pos, (0,-1,0)
        #if shared.debug: print "***fpu1:", fpu
        #self.set_camera(fpu)

        #if shared.debug: print self.pwX.GetResliceOutput().GetSpacing(), imageData.GetSpacing()

        #self.add_axes_labels()

    def add_axes_labels(self):
        #if shared.debug: print "***Adding axes labels"
        #if shared.debug: print labels
        labels = shared.labels
        #labels = list(np.array(labels)[[4,5,2,3,0,1]])
        self.axes_labels=labels
        self.axes_labels_actors=[]
        size = abs(self.imageData.GetSpacing()[0]) * 5
        #if shared.debug: print "***size", size
        for i,b in enumerate(self.imageData.GetBounds()):
            coords = list(self.imageData.GetCenter())
            coords[i/2] = b*1.1
            #Correction for negative spacings
            idx_label = 1*i
            #if self.imageData.GetSpacing()[i/2]<0:
            #    if shared.debug: print "Changing for label no.", idx_label, labels[idx_label]
            #    if idx_label%2==0:
            #        idx_label += 1
            #    else:
            #        idx_label-=1
            label = labels[idx_label]
            if shared.debug: print i,b, coords, label
            #Orientation should be correct due to reading affine in vtkNifti
            text = vtk.vtkVectorText()
            text.SetText(label)
            textMapper = vtk.vtkPolyDataMapper()
            textMapper.SetInput(text.GetOutput())
            textActor = vtk.vtkFollower()
            textActor.SetMapper(textMapper)
            textActor.SetScale(size, size, size)
            x,y,z = coords
            textActor.SetPosition(x, y, z)
            textActor.GetProperty().SetColor((1,1,0))
            textActor.SetCamera(self.camera)
            self.axes_labels_actors.append(textActor)
            self.renderer.AddActor(textActor)

        #Reorient camera to have head up
        center = self.imageData.GetCenter()
        spacing = self.imageData.GetSpacing()
        bounds = np.array(self.imageData.GetBounds())
        if shared.debug: print "***center,spacing,bounds", center,spacing,bounds
        #idx_left = labels.index("L")
        pos = [center[0], center[1], center[2]]
        pos[0] +=  max((bounds[1::2]-bounds[0::2]))*2
        #idx_sup = labels.index("S")
        camera_up = [0,0,0]
        camera_up[2] = 1
        if shared.debug: print idx_sup, camera_up
        fpu = center, pos, tuple(camera_up)
        if shared.debug: print "***fpu2:", fpu
        self.set_camera(fpu)

    def get_marker_at_point(self):
        
        x, y = self.GetEventPosition()
        picker = vtk.vtkPropPicker()
        picker.PickProp(x, y, self.renderer, EventHandler().get_markers())
        actor = picker.GetActor()
        return actor

    def update_viewer(self, event, *args):
        MarkerWindowInteractor.update_viewer(self, event, *args)
        if event=='add marker':
            marker = args[0]
            self.add_marker(marker)
        elif event=='remove marker':
            marker = args[0]
            self.remove_marker(marker)
        elif event=='color marker':
            marker, color = args
            marker.set_color(color)
        elif event=='label marker':
            marker, label = args
            marker.set_label(label)
            
            if shared.debug: print "Create VTK-Text", marker.get_label()
            text = vtk.vtkVectorText()
            text.SetText(marker.get_label())
            textMapper = vtk.vtkPolyDataMapper()
            textMapper.SetInput(text.GetOutput())
            textActor = self.textActors[marker]
            textActor.SetMapper(textMapper)

        elif event=='move marker':
            marker, center = args
            marker.set_center(center)
            #update the select boxes and text actor
            textActor = self.textActors[marker]
            size = marker.get_size()
            textActor.SetScale(size, size, size)
            x,y,z = marker.get_center()
            textActor.SetPosition(x+size, y+size, z+size)

            if self.boxes.has_key(marker):
                selectActor = self.boxes[marker]
                boxSource = vtk.vtkCubeSource()
                boxSource.SetBounds(marker.GetBounds())
                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInput(boxSource.GetOutput())
                selectActor.SetMapper(mapper)
                
        elif event=='labels on':
            actors = self.textActors.values()
            for actor in actors:
                actor.VisibilityOn()
        elif event=='labels off':
            actors = self.textActors.values()
            for actor in actors:
                actor.VisibilityOff()
        elif event=='select marker':
            marker = args[0]
            boxSource = vtk.vtkCubeSource()
            boxSource.SetBounds(marker.GetBounds())
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInput(boxSource.GetOutput())
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor( marker.get_color() )
            actor.GetProperty().SetRepresentationToWireframe()
            actor.GetProperty().SetLineWidth(2.0)
            if shared.debug: print "PlaneWidgetsXYZ.update_viewer(): self.renderer.AddActor(actor)"
            self.renderer.AddActor(actor)
            self.boxes[marker] = actor
        elif event=='unselect marker':
            marker = args[0]
            actor = self.boxes[marker]
            self.renderer.RemoveActor(actor)
        elif event=="set axes directions":
            self.add_axes_labels()
            EventHandler().notify('observers update plane')
        
        self.Render()
    
        
        
    def add_marker(self, marker):
        if shared.debug: print "PlaneWidgetsXYZ.add_marker(): self.renderer.AddActor(marker)"
        self.renderer.AddActor(marker)

        text = vtk.vtkVectorText()
        text.SetText(marker.get_label())
        textMapper = vtk.vtkPolyDataMapper()
        textMapper.SetInput(text.GetOutput())

        textActor = vtk.vtkFollower()
        textActor.SetMapper(textMapper)
        size = marker.get_size()
        textActor.SetScale(size, size, size)
        x,y,z = marker.get_center()
        textActor.SetPosition(x+size, y+size, z+size)
        textActor.SetCamera(self.camera)
        textActor.GetProperty().SetColor(marker.get_label_color())
        if EventHandler().get_labels_on():
            if shared.debug: print "VisibilityOn"
            textActor.VisibilityOn()
        else:
            if shared.debug: print "VisibilityOff"
            textActor.VisibilityOff()


        self.textActors[marker] = textActor
        if shared.debug: print "PlaneWidgetsXYZ.add_marker(): self.renderer.AddActor(textActor)"
        self.renderer.AddActor(textActor)

    def remove_marker(self, marker):
        self.renderer.RemoveActor(marker)
        self.renderer.RemoveActor(self.textActors[marker])
        del self.textActors[marker]

    def _plane_widget_boilerplate(self, pw, key, color, index, orientation):

        if shared.debug: print "PlaneWidgetsXYZ._plane_widget_boilerplate(", index , orientation,")"
        pw.TextureInterpolateOn()
        #pw.SetResliceInterpolateToCubic()
        pw.SetKeyPressActivationValue(key)
        if shared.debug: print "pw " , orientation, ".SetPicker(self.sharedPicker)"
        pw.SetPicker(self.sharedPicker)
        pw.GetPlaneProperty().SetColor(color)
        pw.DisplayTextOn()
        pw.SetInput(self.imageData)
        pw.SetPlaneOrientation(orientation)
        pw.SetSliceIndex(int(index))
        if shared.debug: print "pw " , orientation, ".SetInteractor(self.interactor)"
        pw.SetInteractor(self.interactor)
        pw.On()
        pw.UpdatePlacement()

    def get_plane_widget_x(self):
        return self.pwX

    def get_plane_widget_y(self):
        return self.pwY

    def get_plane_widget_z(self):
        return self.pwZ

    def get_plane_widgets_xyz(self):
        return (self.get_plane_widget_x(),
                self.get_plane_widget_y(),
                self.get_plane_widget_z())

    def snap_view_to_point(self, xyz):

        # project the point onto the plane, find the distance between
        # xyz and the projected point, then move the plane along it's
        # normal that distance

        #todo: undo
        move_pw_to_point(self.pwX, xyz)
        move_pw_to_point(self.pwY, xyz)
        move_pw_to_point(self.pwZ, xyz)
        self.Render()
        EventHandler().notify('observers update plane')
        

    def set_plane_points_xyz(self, pxyz):
        px, py, pz = pxyz
        self.set_plane_points(self.pwX, px)
        self.set_plane_points(self.pwY, py)
        self.set_plane_points(self.pwZ, pz)
        self.Render()
        EventHandler().notify('observers update plane')

    def set_select_mode(self):
        self.interactButtons = (2,3)

    def set_interact_mode(self):
        self.interactButtons = (1,2,3)

    def OnButtonDown(self, wid, event):
        """Mouse button pressed."""

        #if shared.debug: print "PlaneWidgetsXYZ.OnButtonDown(): event=", event

        self.lastPntsXYZ = ( self.get_plane_points(self.pwX),
                             self.get_plane_points(self.pwY),
                             self.get_plane_points(self.pwZ))
        #if shared.debug: print "PlaneWidgetsXYZ.OnButtonDown(): self.lastPntsXYZ=", self.lastPntsXYZ
                             

        MarkerWindowInteractor.OnButtonDown(self, wid, event)
        #if shared.debug: print self.axes_labels
        return True

    def OnButtonUp(self, wid, event):
        """Mouse button released."""
        
        if shared.debug: print "PlaneWidgetsXYZ.OnButtonUp(): event=", event

        if not hasattr(self, 'lastPntsXYZ'): return
        MarkerWindowInteractor.OnButtonUp(self, wid, event)
        pntsXYZ = ( self.get_plane_points(self.pwX),
                    self.get_plane_points(self.pwY),
                    self.get_plane_points(self.pwZ))


        if pntsXYZ != self.lastPntsXYZ:
            UndoRegistry().push_command(
                self.set_plane_points_xyz, self.lastPntsXYZ)


        return True


