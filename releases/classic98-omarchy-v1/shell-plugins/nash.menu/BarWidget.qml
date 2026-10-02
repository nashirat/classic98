import QtQuick
import Quickshell
import qs.Commons
import qs.Ui

BarWidget {
  id: root
  moduleName: "omarchy.menu"

  implicitWidth: button.implicitWidth + (Color.pick("classic98.enabled", "false") === "true" ? 13 : 0)
  implicitHeight: button.implicitHeight

  ClassicButton {
    id: button
    anchors.fill: parent
    anchors.rightMargin: Color.pick("classic98.enabled", "false") === "true" ? 13 : 0
    leadingIcon: "file://" + Quickshell.env("HOME") + "/.local/state/omarchy/current/theme/icons/windows-start.png"
    bar: root.bar
    text: classic98 ? "Start" : "\ue900"
    fontFamily: "omarchy"
    fontBold: classic98
    horizontalMargin: classic98 ? 14 : 7.5
    onPressed: function(button) {
      if (!root.bar) return
      if (button === Qt.RightButton) root.bar.run("xdg-terminal-exec")
      else root.bar.run("omarchy-shell shell toggle omarchy.menu '{\"menu\":\"root\"}'")
    }
  }
  Item {
    visible: Color.pick("classic98.enabled", "false") === "true"
    anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter
    anchors.rightMargin: 4
    width: 6; height: 22
    Rectangle { x: 1; y: 2; width: 1; height: 18; color: "#808080" }
    Rectangle { x: 2; y: 2; width: 1; height: 18; color: "#ffffff" }
    Rectangle { x: 4; y: 2; width: 1; height: 18; color: "#808080" }
    Rectangle { x: 5; y: 2; width: 1; height: 18; color: "#ffffff" }
  }
}
