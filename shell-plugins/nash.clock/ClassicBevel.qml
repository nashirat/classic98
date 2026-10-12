import QtQuick
// Raised/sunken edges in the active window frame palette: light #676767, dark #202020.
Item {
  id: root
  property bool sunken: false
  property bool shallow: false
  property color light: sunken ? "#202020" : "#676767"
  property color dark: sunken ? "#676767" : "#202020"
  Rectangle { x: 0; y: 0; width: parent.width; height: 1; color: root.light }
  Rectangle { x: 0; y: 0; width: 1; height: parent.height; color: root.light }
  Rectangle { x: 0; y: parent.height - 1; width: parent.width; height: 1; color: root.dark }
  Rectangle { x: parent.width - 1; y: 0; width: 1; height: parent.height; color: root.dark }
  Item {
    visible: !root.shallow
    anchors.fill: parent; anchors.margins: 1
    Rectangle { x: 0; y: 0; width: parent.width; height: 1; color: root.sunken ? "#383838" : "#5a5a5a" }
    Rectangle { x: 0; y: 0; width: 1; height: parent.height; color: root.sunken ? "#383838" : "#5a5a5a" }
    Rectangle { x: 0; y: parent.height - 1; width: parent.width; height: 1; color: root.sunken ? "#5a5a5a" : "#383838" }
    Rectangle { x: parent.width - 1; y: 0; width: 1; height: parent.height; color: root.sunken ? "#5a5a5a" : "#383838" }
  }
}
