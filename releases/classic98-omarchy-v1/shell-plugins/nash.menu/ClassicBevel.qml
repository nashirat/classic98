import QtQuick
Item {
  id: root
  property bool sunken: false
  property bool shallow: false
  property color light: sunken ? "#808080" : "#ffffff"
  property color dark: sunken ? "#ffffff" : "#000000"
  Rectangle { x: 0; y: 0; width: parent.width; height: 1; color: root.light }
  Rectangle { x: 0; y: 0; width: 1; height: parent.height; color: root.light }
  Rectangle { x: 0; y: parent.height - 1; width: parent.width; height: 1; color: root.dark }
  Rectangle { x: parent.width - 1; y: 0; width: 1; height: parent.height; color: root.dark }
  Item {
    visible: !root.shallow
    anchors.fill: parent; anchors.margins: 1
    Rectangle { x: 0; y: 0; width: parent.width; height: 1; color: root.sunken ? "#000000" : "#dfdfdf" }
    Rectangle { x: 0; y: 0; width: 1; height: parent.height; color: root.sunken ? "#000000" : "#dfdfdf" }
    Rectangle { x: 0; y: parent.height - 1; width: parent.width; height: 1; color: root.sunken ? "#dfdfdf" : "#808080" }
    Rectangle { x: parent.width - 1; y: 0; width: 1; height: parent.height; color: root.sunken ? "#dfdfdf" : "#808080" }
  }
}
