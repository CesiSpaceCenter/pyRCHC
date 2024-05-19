from __future__ import annotations
from PyQt6 import QtWidgets
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import *
from PyQt6.Qt3DCore import *
from PyQt6.Qt3DExtras import *
from PyQt6.Qt3DRender import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from window import MainWindow


class RocketView3D(Qt3DWindow):
    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y() / -20
        lens = self.camera().lens()
        fov = lens.fieldOfView()
        new_fov = fov + delta
        if new_fov not in range(20, 120):  # limit zoom
            return
        lens.setFieldOfView(new_fov)


def create_bar(root_entity) -> (QEntity, QTransform, QCylinderMesh):  # bars for the x y z axis
    bar_entity = QEntity(root_entity)
    bar_mesh = QCylinderMesh(None)
    bar_mesh.setLength(50)
    bar_mesh.setRadius(0.1)
    bar_mesh.setSlices(4)
    bar_transform = QTransform()
    bar_material = QPhongMaterial(root_entity)
    bar_material.setShininess(0)
    bar_entity.addComponent(bar_mesh)
    bar_entity.addComponent(bar_transform)
    bar_entity.addComponent(bar_material)
    return bar_entity, bar_transform, bar_material, bar_mesh


def create_scene(model_file: str) -> tuple[QEntity, QTransform]:
    root_entity = QEntity()

    # create the rocket enity with its mesh, material and transform

    rocket_entity = QEntity(root_entity)
    rocket_mesh = QMesh(None)
    rocket_mesh.setSource(QUrl.fromLocalFile(model_file))  # load the 3d model into the mesh

    rocket_material = QPhongMaterial(None)
    rocket_material.setDiffuse(QColorConstants.LightGray)

    rocket_transform = QTransform()
    rocket_transform.setTranslation(QVector3D(-1, 0, 0))
    rocket_entity.addComponent(rocket_transform)

    # https://stackoverflow.com/questions/51742892/animating-a-qt3d-rotation-around-a-specific-axis

    rocket_entity.addComponent(rocket_mesh)
    rocket_entity.addComponent(rocket_material)

    x_bar_entity, x_bar_transform, x_bar_material, x_bar_mesh = create_bar(root_entity)
    x_bar_transform.setRotationZ(90)
    x_bar_transform.setTranslation(QVector3D(x_bar_mesh.length() / 2, 0, 0))
    x_bar_material.setAmbient(QColorConstants.Red)
    x_bar_material.setDiffuse(QColorConstants.Red)

    y_bar_entity, y_bar_transform, y_bar_material, y_bar_mesh = create_bar(root_entity)
    y_bar_transform.setRotationX(90)
    y_bar_transform.setTranslation(QVector3D(0, 0, -y_bar_mesh.length() / 2))
    y_bar_material.setAmbient(QColorConstants.Green)
    y_bar_material.setDiffuse(QColorConstants.Green)

    z_bar_entity, z_bar_transform, z_bar_material, z_bar_mesh = create_bar(root_entity)
    z_bar_transform.setTranslation(QVector3D(0, z_bar_mesh.length() / 2, 0))
    z_bar_material.setAmbient(QColorConstants.Blue)
    z_bar_material.setDiffuse(QColorConstants.Blue)

    return root_entity, rocket_transform


class Scene3D:
    def __init__(self, window: MainWindow, _parent: QtWidgets.QWidget, _parent_grid: QtWidgets.QLayout, properties: dict):
        self.window = window
        self.properties = properties

        view_3d = RocketView3D(None)
        # set the background of the scene to be the same as the background of the window
        # TODO: do this automatically (from the stylesheet)
        background_color = QColor().fromRgb(238, 238, 238)
        view_3d.defaultFrameGraph().setClearColor(background_color)
        self.element = QtWidgets.QWidget.createWindowContainer(view_3d)

        self.view_scene, self.rocket_transform = create_scene(properties['model'])
        if 'scale' in properties:  # scale the model if needed
            self.rocket_transform.setScale(properties['scale'])

        view_cam = view_3d.camera()
        view_cam.lens().setPerspectiveProjection(50, 16 / 9, 0.1, 1000)
        view_cam.setPosition(QVector3D(30, 30, -30))
        view_cam.setViewCenter(QVector3D(0, 0, 0))

        cam_ctrl = QOrbitCameraController(self.view_scene)
        cam_ctrl.setLinearSpeed(0)  # disable translating the camera
        cam_ctrl.setLookSpeed(-500)  # negative so it feels like we are "grabbing" the view (more natural)
        cam_ctrl.setCamera(view_cam)

        view_3d.setRootEntity(self.view_scene)
        view_3d.show()

    def set_data(self, data):
        if 'data' in self.properties:
            data_properties = self.properties['data']
            # -90 so the rocket is upright (probably not right)
            self.rocket_transform.setRotationX(data[data_properties['roll']] - 90)
            self.rocket_transform.setRotationY(data[data_properties['pitch']])
            self.rocket_transform.setRotationZ(data[data_properties['yaw']])
