from pathlib import Path
import shutil
root=Path(__file__).resolve().parent
plugins=root/'shell-plugins'
plugins.mkdir(exist_ok=True)
for name in ('menu','workspaces','clock','bar','active-window'):
    source=Path('/home/nash/.config/omarchy/plugins')/('nash.'+name)
    target=plugins/source.name
    if not target.exists(): shutil.copytree(source,target)
bevel='''import QtQuick
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
'''
base=Path('/usr/share/omarchy/shell/Ui/WidgetButton.qml').read_text()
base=base.replace('  function triggerPress(button) {','''  readonly property bool classic98: Color.bar.background.toString() === "#c0c0c0"
  property bool sunken: false
  property bool shallow: false
  property bool clickPulse: false
  readonly property bool depressed: sunken || mouseArea.pressed || clickPulse
  Timer { id: clickTimer; interval: 130; onTriggered: root.clickPulse = false }
  function triggerPress(button) {
    root.clickPulse = true
    clickTimer.restart()''')
base=base.replace('  Text {\n    id: label','''  Rectangle {
    visible: root.classic98
    anchors.fill: parent
    anchors.margins: 3
    color: root.sunken ? "#dfdfdf" : "#c0c0c0"
    ClassicBevel { anchors.fill: parent; sunken: root.depressed; shallow: root.shallow }
  }
  Text {
    id: label''')
base=base.replace('    anchors.centerIn: parent\n    text: root.text','''    anchors.centerIn: parent
    anchors.horizontalCenterOffset: root.classic98 && root.depressed ? 1 : 0
    anchors.verticalCenterOffset: root.classic98 && root.depressed ? 1 : 0
    text: root.text''')
base=base.replace('    font.family: root.fontFamily','    font.family: root.classic98 ? "Microsoft Sans Serif" : root.fontFamily')
for name in ('nash.menu','nash.workspaces','nash.clock'):
    folder=plugins/name
    (folder/'ClassicBevel.qml').write_text(bevel)
    (folder/'ClassicButton.qml').write_text(base)
menu=plugins/'nash.menu'/'BarWidget.qml'
text=menu.read_text().replace('WidgetButton {','ClassicButton {')
text=text.replace('text: "\\ue900"', 'text: classic98 ? "Start" : "\\ue900"')
text=text.replace('horizontalMargin: 7.5','horizontalMargin: classic98 ? 14 : 7.5')
menu.write_text(text)
ws=plugins/'nash.workspaces'/'Workspaces.qml'
text=ws.read_text().replace('WidgetButton {','ClassicButton {')
text=text.replace('text: focused ? "\\uDB85\\uDCFB" : (modelData === 10 ? "0" : String(modelData))','text: classic98 ? String(modelData) : (focused ? "\\uDB85\\uDCFB" : (modelData === 10 ? "0" : String(modelData)))\n        sunken: classic98 && focused')
text=text.replace('opacity: occupied || focused ? 1 : 0.5','opacity: classic98 || occupied || focused ? 1 : 0.5')
text=text.replace('fixedWidth: root.vertical ? root.barSize : Style.space(20)','fixedWidth: root.vertical ? root.barSize : (classic98 ? 30 : Style.space(20))')
ws.write_text(text)
clock=plugins/'nash.clock'/'BarWidget.qml'
text=clock.read_text().replace('WidgetButton {','ClassicButton {').replace('    id: button','    id: button\n    sunken: classic98\n    shallow: true')
clock.write_text(text)
bar=plugins/'nash.bar'/'Bar.qml'
text=bar.read_text().replace('  property string fontFamily: Style.font.family','  property string fontFamily: Color.bar.background.toString() === "#c0c0c0" ? "Microsoft Sans Serif" : Style.font.family')
marker='    WlrLayershell.layer: WlrLayer.Top\n'
text=text.replace(marker, marker+'''
    // Classic taskbar raised top seam; widgets retain all stock behavior.
    Rectangle {
      visible: Color.bar.background.toString() === "#c0c0c0"
      anchors.top: parent.top
      width: parent.width; height: 1; color: "#dfdfdf"; z: 100
    }
    Rectangle {
      visible: Color.bar.background.toString() === "#c0c0c0"
      y: 1; width: parent.width; height: 1; color: "#ffffff"; z: 100
    }
''')
bar.write_text(text)
active=plugins/'nash.active-window'/'ActiveWindow.qml'
folder=active.parent
(folder/'ClassicBevel.qml').write_text(bevel)
text=active.read_text().replace('  Item {\n    anchors.fill: parent','''  Rectangle {
    visible: Color.bar.background.toString() === "#c0c0c0"
    anchors.fill: parent; anchors.margins: 3
    color: "#dfdfdf"
    ClassicBevel { anchors.fill: parent; sunken: true }
  }
  Item {
    anchors.fill: parent''',1)
text=text.replace('      opacity: 0.85','      opacity: 1.0')
active.write_text(text)
print('Prepared classic shell plugins:',plugins)
