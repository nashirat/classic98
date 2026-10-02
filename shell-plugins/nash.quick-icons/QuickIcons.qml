import QtQuick
import QtQuick.Layouts
import qs.Ui

BarWidget {
  id: root
  moduleName: "nash.quick-icons"
  implicitWidth: grid.implicitWidth + (root.vertical ? 0 : 13)
  implicitHeight: grid.implicitHeight

  GridLayout {
    id: grid
    anchors.left: parent.left
    anchors.verticalCenter: parent.verticalCenter
    columns: root.vertical ? 1 : 4
    columnSpacing: 2
    rowSpacing: 2
    Repeater {
      model: [
        { icon: "internet-explorer", label: "Chrome", command: "omarchy launch browser" },
        { icon: "email", label: "Gmail", command: "omarchy launch browser https://mail.google.com/" },
        { icon: "paint", label: "Figma (later)", command: "" },
        { icon: "phone", label: "WhatsApp", command: "omarchy launch browser https://web.whatsapp.com/" }
      ]
      BarIconButton {
        id: shortcut
        required property var modelData
        bar: root.bar
        slotSize: 26
        opticalSize: 20
        tooltipText: modelData.label
        pressable: modelData.command !== ""
        iconComponent: Image {
          source: Qt.resolvedUrl("icons/" + shortcut.modelData.icon + ".png")
          smooth: false
          fillMode: Image.PreserveAspectFit
        }
        onPressed: function(button) {
          if (button === Qt.LeftButton && root.bar && modelData.command !== "")
            root.bar.run(modelData.command)
        }
      }
    }
  }
  Item {
    visible: !root.vertical
    anchors.right: parent.right
    anchors.verticalCenter: parent.verticalCenter
    anchors.rightMargin: 4
    width: 6
    height: 22
    Rectangle { x: 1; y: 2; width: 1; height: 18; color: "#808080" }
    Rectangle { x: 2; y: 2; width: 1; height: 18; color: "#ffffff" }
    Rectangle { x: 4; y: 2; width: 1; height: 18; color: "#808080" }
    Rectangle { x: 5; y: 2; width: 1; height: 18; color: "#ffffff" }
  }
}
