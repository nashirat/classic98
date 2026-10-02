import QtQuick
import qs.Commons

Item {
  id: root

  property var bar: null
  property string text: ""
  property string fontFamily: bar ? bar.fontFamily : Style.font.family
  property real fontSize: Style.font.body
  property color foreground: bar ? bar.barForeground : Color.foreground
  property color activeColor: bar ? bar.urgent : Color.urgent
  property bool active: false
  property real horizontalMargin: 8.5
  property real verticalPadding: 6
  property real fixedWidth: -1
  property real fixedHeight: -1
  property real textRotation: 0
  property bool keepSpace: false
  property bool dimmed: false
  property bool concealed: false
  property bool interactive: true
  property bool pressable: true
  property bool useActiveColor: true
  property bool maintainIndicatorReveal: false
  property bool labelVisible: true
  property bool hasVisualContent: text !== ""
  property var revealHost: bar
  property string tooltipText: ""
  property var registeredBar: null

  signal pressed(int button)
  signal wheelMoved(int delta)

  readonly property bool classic98: Color.pick("classic98.enabled", "false") === "true"
  property bool sunken: false
  property bool shallow: false
  property bool clickPulse: false
  readonly property bool depressed: sunken || mouseArea.pressed || clickPulse
  Timer { id: clickTimer; interval: 130; onTriggered: root.clickPulse = false }
  function triggerPress(button) {
    root.clickPulse = true
    clickTimer.restart()
    if (root.bar) root.bar.hideTooltip(root)
    root.pressed(button)
  }

  function hideOwnTooltip() {
    if (root.bar) root.bar.hideTooltip(root)
  }

  function syncClickRegistration() {
    if (registeredBar && registeredBar.unregisterClickTarget) registeredBar.unregisterClickTarget(root)
    registeredBar = root.bar
    if (registeredBar && registeredBar.registerClickTarget) registeredBar.registerClickTarget(root)
  }

  onBarChanged: syncClickRegistration()
  onVisibleChanged: if (!visible) hideOwnTooltip()
  onInteractiveChanged: if (!interactive) hideOwnTooltip()
  onConcealedChanged: if (concealed) hideOwnTooltip()
  Component.onCompleted: syncClickRegistration()
  Component.onDestruction: if (registeredBar && registeredBar.unregisterClickTarget) registeredBar.unregisterClickTarget(root)

  readonly property bool vertical: bar ? bar.vertical : false
  readonly property int barSize: bar ? bar.barSize : Style.bar.sizeHorizontal
  readonly property real scaledHorizontalMargin: Style.spaceReal(horizontalMargin)
  readonly property real scaledVerticalPadding: Style.spaceReal(verticalPadding)
  readonly property bool tooltipHovered: visible && interactive && !concealed && mouseArea.containsMouse
  // Width of the painted label, for bar chrome that wants to line up with the
  // text rather than with the slot it sits in. Zero on icon-only buttons.
  readonly property real labelWidth: label.visible ? label.implicitWidth : 0

  visible: hasVisualContent || keepSpace
  opacity: !hasVisualContent || concealed ? 0 : (dimmed ? 0.45 : 1)
  implicitWidth: fixedWidth > 0 ? fixedWidth : (vertical ? barSize : Math.max(12, label.implicitWidth + scaledHorizontalMargin * 2))
  implicitHeight: fixedHeight > 0 ? fixedHeight : (vertical ? Math.max(12, label.implicitHeight + scaledVerticalPadding * 2) : barSize)

  Behavior on opacity {
    NumberAnimation { duration: 140; easing.type: Easing.OutCubic }
  }

  Rectangle {
    visible: root.classic98
    anchors.fill: parent
    anchors.margins: 3
    anchors.topMargin: 5
    anchors.bottomMargin: 5
    color: root.sunken ? "#dfdfdf" : "#c0c0c0"
    Image {
      visible: root.sunken
      anchors.fill: parent
      anchors.margins: 2
      source: "checker.svg"
      sourceSize.width: 2
      sourceSize.height: 2
      fillMode: Image.Tile
      smooth: false
      mipmap: false
    }
    ClassicBevel { anchors.fill: parent; sunken: root.depressed; shallow: root.shallow }
  }
  Text {
    id: label
    textFormat: Text.PlainText
    visible: root.labelVisible
    anchors.centerIn: parent
    anchors.horizontalCenterOffset: root.classic98 && root.depressed ? 1 : 0
    anchors.verticalCenterOffset: root.classic98 && root.depressed ? 1 : 0
    text: root.text
    color: root.active && root.useActiveColor ? root.activeColor : root.foreground
    font.family: root.classic98 ? "Microsoft Sans Serif" : root.fontFamily
    font.pixelSize: root.fontSize
    renderType: Text.NativeRendering
    rotation: root.textRotation
    horizontalAlignment: Text.AlignHCenter
    verticalAlignment: Text.AlignVCenter

    Behavior on color {
      enabled: !root.bar || root.bar.foregroundAnimationEnabled
      ColorAnimation { duration: 160 }
    }
  }

  MouseArea {
    id: mouseArea
    anchors.fill: parent
    acceptedButtons: Qt.LeftButton | Qt.RightButton | Qt.MiddleButton
    enabled: root.interactive
    hoverEnabled: true
    cursorShape: root.pressable ? Qt.PointingHandCursor : Qt.ArrowCursor
    onEntered: {
      if (root.bar) {
        root.bar.showTooltip(root, root.tooltipText)
      }
      if (root.maintainIndicatorReveal && root.revealHost && root.revealHost.setIndicatorItemHovered)
        root.revealHost.setIndicatorItemHovered(true)
    }
    onExited: {
      if (root.bar) {
        root.bar.hideTooltip(root)
      }
      if (root.maintainIndicatorReveal && root.revealHost && root.revealHost.setIndicatorItemHovered)
        root.revealHost.setIndicatorItemHovered(false)
    }
    onClicked: function(mouse) { if (root.pressable) root.triggerPress(mouse.button) }
    onWheel: function(wheel) { root.wheelMoved(wheel.angleDelta.y) }
  }
}
