from __future__ import annotations
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.Qt3DExtras import *
from PyQt6.Qt3DCore import *
from PyQt6.Qt3DRender import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from window import MainWindow


class RocketView3D(Qt3DWindow):
    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y() / -20.0
        lens = self.camera().lens()
        fov = lens.fieldOfView()
        newFov = min(max(fov + delta, 20.0), 120.0)
        lens.setFieldOfView(newFov)


def createScene():
    rootEntity = QEntity()

    # Full bright (shadeless)
    # rocketMaterial.setAmbient(Qt.red)
    # rocketMaterial.setDiffuse(Qt.red)
    # rocketMaterial.setShininess(0)

    rocketEntity = QEntity(rootEntity)
    rocketMesh = QMesh()
    rocketMesh.setSource(QUrl.fromLocalFile('cesinova.obj'))

    rocketColor = QColor()
    rocketColor.setRgb(255, 255, 255)

    rocketMaterial = QPhongMaterial()
    rocketMaterial.setDiffuse(rocketColor)

    rocketTransform: QComponent = QTransform()
    rocketEntity.addComponent(rocketTransform)

    rocketTransform.scale(0.04, 0.04)
    # https://stackoverflow.com/questions/51742892/animating-a-qt3d-rotation-around-a-specific-axis

    rocketEntity.addComponent(rocketMesh)
    rocketEntity.addComponent(rocketMaterial)

    xBarEntity = QEntity(rootEntity)
    xBarMesh = QCylinderMesh()
    xBarMesh.setLength(50)
    xBarMesh.setRadius(0.1)
    xBarMesh.setSlices(4)
    xBarTransform = QTransform()
    xBarTransform.setRotation(QQuaternion.fromEulerAngles(0, 0, 90))
    xBarTransform.setTranslation(QVector3D(xBarMesh.length() / 2, 0, 0))
    xBarMaterial = QPhongMaterial(rootEntity)
    xBarMaterial.setAmbient(Qt.red)
    xBarMaterial.setDiffuse(Qt.red)
    xBarMaterial.setShininess(0)
    xBarEntity.addComponent(xBarMesh)
    xBarEntity.addComponent(xBarTransform)
    xBarEntity.addComponent(xBarMaterial)

    yBarEntity = QEntity(rootEntity)
    yBarMesh = QCylinderMesh()
    yBarMesh.setLength(50)
    yBarMesh.setRadius(0.1)
    yBarMesh.setSlices(4)
    yBarTransform = QTransform()
    yBarTransform.setRotation(QQuaternion.fromEulerAngles(90, 0, 0))
    yBarTransform.setTranslation(QVector3D(0, 0, -yBarMesh.length() / 2))
    yBarMaterial = QPhongMaterial(rootEntity)
    yBarMaterial.setAmbient(Qt.green)
    yBarMaterial.setDiffuse(Qt.green)
    yBarMaterial.setShininess(0)
    yBarEntity.addComponent(yBarMesh)
    yBarEntity.addComponent(yBarTransform)
    yBarEntity.addComponent(yBarMaterial)

    zBarEntity = QEntity(rootEntity)
    zBarMesh = QCylinderMesh()
    zBarMesh.setLength(50)
    zBarMesh.setRadius(0.1)
    zBarMesh.setSlices(4)
    zBarTransform = QTransform()
    zBarTransform.setTranslation(QVector3D(0, zBarMesh.length() / 2, 0))
    zBarMaterial = QPhongMaterial(rootEntity)
    zBarMaterial.setAmbient(Qt.blue)
    zBarMaterial.setDiffuse(Qt.blue)
    zBarMaterial.setShininess(0)
    zBarEntity.addComponent(zBarMesh)
    zBarEntity.addComponent(zBarTransform)
    zBarEntity.addComponent(zBarMaterial)

    return rootEntity, rocketTransform, rocketEntity


class Scene3D:
    def __init__(self, window: MainWindow, parent: QtWidgets.QWidget, parent_grid: QtWidgets.QLayout, properties: dict):
        self.window = window
        self.properties = properties

        view3D = self.view3D = RocketView3D()
        view3D.renderSettings().setRenderPolicy(QRenderSettings.RenderPolicy.OnDemand)
        viewContainer = self.element = QtWidgets.QWidget.createWindowContainer(view3D)

        self.viewScene, self.rocketTransform, self.rocketEntity = createScene()

        # Camera
        viewCam = self.viewCam = view3D.camera()
        viewCam.lens().setPerspectiveProjection(50.0, 16.0 / 9.0, 0.1, 1000.0)
        viewCam.setPosition(QVector3D(30.0, 30.0, -30.0))
        viewCam.setViewCenter(QVector3D(0.0, 0.0, 0.0))

        # Camera controls
        camCtrl = self.viewCamCtrl = QOrbitCameraController(self.viewScene)
        camCtrl.setLinearSpeed(0)
        camCtrl.setLookSpeed(-200.0)
        camCtrl.setCamera(self.viewCam)

        view3D.setRootEntity(self.viewScene)
        view3D.show()

    def set_data(self, data):
        pass
