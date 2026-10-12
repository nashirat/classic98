import QtQuick
import QtQuick.Layouts
import Quickshell.Hyprland
import qs.Commons
import qs.Ui

BarWidget {
  id: root
  moduleName: "omarchy.workspaces"

  function workspaceById(id) {
    var values = Hyprland.workspaces.values
    for (var i = 0; i < values.length; i++) {
      if (values[i].id === id) return values[i]
    }

    return null
  }

  function workspaceIds() {
    var ids = [1, 2, 3, 4, 5]
    var values = Hyprland.workspaces.values

    for (var i = 0; i < values.length; i++) {
      var id = values[i].id
      if (id > 0 && id <= 10 && ids.indexOf(id) === -1) ids.push(id)
    }

    ids.sort(function(left, right) { return left - right })
    return ids
  }

  function focusWorkspace(id) {
    if (!root.bar) return
    root.bar.run("hyprctl dispatch " + Util.shellQuote("hl.dsp.focus({ workspace = \"" + id + "\" })"))
  }

  readonly property real trailingGap: root.vertical ? 0 : Style.spaceReal(1.5)

  readonly property bool classic98: Color.pick("classic98.enabled", "false") === "true"
  readonly property real dividerSpace: classic98 && !root.vertical ? 13 : 0

  implicitWidth: grid.implicitWidth + trailingGap + 2 * dividerSpace
  implicitHeight: grid.implicitHeight

  GridLayout {
    id: grid
    anchors.fill: parent
    anchors.leftMargin: root.dividerSpace
    anchors.rightMargin: root.trailingGap + root.dividerSpace
    columns: root.vertical ? 1 : root.workspaceIds().length
    columnSpacing: root.vertical ? 0 : Style.space(1)
    rowSpacing: root.vertical ? Style.space(2) : 0

    Repeater {
      model: root.workspaceIds()

      ClassicButton {
        required property int modelData

        readonly property var workspace: root.workspaceById(modelData)
        readonly property bool occupied: workspace !== null && workspace.toplevels.values.length > 0
        readonly property bool focused: Hyprland.focusedWorkspace !== null && Hyprland.focusedWorkspace.id === modelData

        bar: root.bar
        text: classic98 ? String(modelData) : (focused ? "\uDB85\uDCFB" : (modelData === 10 ? "0" : String(modelData)))
        sunken: classic98 && focused
        opacity: classic98 || occupied || focused ? 1 : 0.5
        horizontalMargin: 6
        verticalPadding: 6
        fixedWidth: root.vertical ? root.barSize : (classic98 ? 30 : Style.space(20))
        fixedHeight: root.barSize
        onPressed: function() { root.focusWorkspace(modelData) }
      }
    }
  }
  Item {
    visible: root.classic98 && !root.vertical
    anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter
    anchors.leftMargin: 4
    width: 6; height: 22
    Rectangle { x: 1; y: 2; width: 1; height: 18; color: "#202020" }
    Rectangle { x: 2; y: 2; width: 1; height: 18; color: "#676767" }
    Rectangle { x: 4; y: 2; width: 1; height: 18; color: "#202020" }
    Rectangle { x: 5; y: 2; width: 1; height: 18; color: "#676767" }
  }
  Item {
    visible: root.classic98 && !root.vertical
    anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter
    anchors.rightMargin: 4
    width: 6; height: 22
    Rectangle { x: 1; y: 2; width: 1; height: 18; color: "#202020" }
    Rectangle { x: 2; y: 2; width: 1; height: 18; color: "#676767" }
    Rectangle { x: 4; y: 2; width: 1; height: 18; color: "#202020" }
    Rectangle { x: 5; y: 2; width: 1; height: 18; color: "#676767" }
  }

}
