from pathlib import Path
import shutil,json
root=Path(__file__).resolve().parent
plugins=root/'shell-plugins'
expressions={
'audio':'root.outputMuted ? "audio-volume-muted.png" : (root.outputVolume < 0.25 ? "audio-volume-low.png" : (root.outputVolume < 0.65 ? "audio-volume-medium.png" : "audio-volume-high.png"))',
'network':'root.kind === "disconnected" ? "network-offline.png" : "network-idle.png"',
'power':'"battery-" + String(Math.round(root.batteryFraction * 5) * 20).padStart(3, "0") + (root.charging ? "-charging" : "") + ".png"',
'monitor':'"display.png"',
'bluetooth':'root.adapter && root.adapter.enabled ? "bluetooth-active.png" : "bluetooth-disabled.png"',
}
for name,expr in expressions.items():
    folder=plugins/('nash.'+name)
    if not folder.exists():shutil.copytree(Path('/home/nash/.config/omarchy/plugins')/folder.name,folder)
    path=folder/'Panel.qml'
    s=path.read_text()
    if 'id: classicPixelIcon' in s:continue
    marker='  BarIconButton {\n    id: button'
    component='''  Component {
    id: classicPixelIcon
    Item {
      Image {
        anchors.centerIn: parent
        width: 20; height: 20
        source: "file://" + Quickshell.env("HOME") + "/.local/state/omarchy/current/theme/icons/" + (EXPR)
        fillMode: Image.PreserveAspectFit
        smooth: false
        mipmap: false
      }
    }
  }

'''.replace('EXPR',expr)
    extra='''
    readonly property bool classic98: Color.pick("classic98.enabled", "false") === "true"
    iconComponent: classic98 ? classicPixelIcon : null
    opticalSize: classic98 ? 20 : Style.bar.iconCanvas
'''
    if name=='power':
        extra=extra.replace('iconComponent: classic98 ?', 'iconComponent: classic98 && !root.showPercentage ?')
        s=s.replace('slotSize: Style.bar.iconSlot * (root.showPercentage && !vertical ? 2 : 1)', 'slotSize: classic98 && !root.showPercentage ? 26 : Style.bar.iconSlot * (root.showPercentage && !vertical ? 2 : 1)')
        s=s.replace('    tooltipText: ""','    tooltipText: Math.round(root.batteryFraction * 100) + "%"',1)
    else:
        extra+='    slotSize: classic98 ? 26 : Style.bar.iconSlot\n'
    s=s.replace(marker,component+marker+extra,1)
    path.write_text(s)
# One recessed tray housing encompasses the icons and clock.
bar=plugins/'nash.bar'
shutil.copy2(plugins/'nash.clock'/'ClassicBevel.qml',bar/'ClassicBevel.qml')
path=bar/'Bar.qml';s=path.read_text()
marker='  component RightModules: ModuleList {\n    entries: root.layoutEntries("right")\n    region: "right"\n  }'
replacement='''  component RightModules: ModuleList {
    entries: root.layoutEntries("right")
    region: "right"
    Rectangle {
      visible: Color.pick("classic98.enabled", "false") === "true"
      z: -1
      anchors.fill: parent
      anchors.topMargin: 3; anchors.bottomMargin: 3
      color: "#c0c0c0"
      ClassicBevel { anchors.fill: parent; sunken: true; shallow: true }
    }
  }'''
assert marker in s or replacement in s
s=s.replace(marker,replacement)
path.write_text(s)
# The clock uses the shared tray's inset instead of a second box.
path=plugins/'nash.clock'/'ClassicButton.qml';s=path.read_text()
s=s.replace('  property bool sunken: false','  property bool paintChrome: true\n  property bool sunken: false')
s=s.replace('    visible: root.classic98\n    anchors.fill: parent','    visible: root.classic98 && root.paintChrome\n    anchors.fill: parent')
path.write_text(s)
path=plugins/'nash.clock'/'BarWidget.qml';s=path.read_text().replace('    shallow: true','    shallow: true\n    paintChrome: false');path.write_text(s)
# Windows flag icon beside Start, with the narrow grip shown in the reference.
path=plugins/'nash.menu'/'ClassicButton.qml';s=path.read_text()
s=s.replace('  property bool sunken: false','  property url leadingIcon: ""\n  property bool sunken: false')
s=s.replace('label.implicitWidth + scaledHorizontalMargin * 2','label.implicitWidth + scaledHorizontalMargin * 2 + (root.classic98 && root.leadingIcon.toString() !== "" ? 16 : 0)')
s=s.replace('anchors.horizontalCenterOffset: root.classic98 && root.depressed ? 1 : 0','anchors.horizontalCenterOffset: (root.classic98 && root.depressed ? 1 : 0) + (root.classic98 && root.leadingIcon.toString() !== "" ? 8 : 0)')
s=s.replace('  Text {\n    id: label','''  Image {
    visible: root.classic98 && root.leadingIcon.toString() !== ""
    x: 9 + (root.depressed ? 1 : 0)
    anchors.verticalCenter: parent.verticalCenter
    width: 16; height: 16
    source: root.leadingIcon
    smooth: false; mipmap: false
  }
  Text {
    id: label''')
path.write_text(s)
path=plugins/'nash.menu'/'BarWidget.qml';s=path.read_text()
s=s.replace('import QtQuick\n','import QtQuick\nimport Quickshell\nimport qs.Commons\n')
s=s.replace('implicitWidth: button.implicitWidth','implicitWidth: button.implicitWidth + (Color.pick("classic98.enabled", "false") === "true" ? 13 : 0)')
s=s.replace('    bar: root.bar','    anchors.rightMargin: Color.pick("classic98.enabled", "false") === "true" ? 13 : 0\n    leadingIcon: "file://" + Quickshell.env("HOME") + "/.local/state/omarchy/current/theme/icons/windows-start.png"\n    bar: root.bar',1)
s=s[:-2]+'''  Item {
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
'''
path.write_text(s)
# Track all icon widgets in the saved theme layout so switching back keeps them.
config=json.loads(Path('/home/nash/.config/omarchy/shell.json').read_text())
(root/'desktop-config/classic-shell.json').write_text(json.dumps(config,indent=2)+'\n')
print('Prepared state-aware tray icons, shared inset, and Menu icon/grip.')
