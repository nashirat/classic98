#!/bin/bash
set -euo pipefail
# Run with pkexec when called from the desktop; sudo is also supported.
[[ $EUID == 0 ]] || { echo 'Run with pkexec or sudo.' >&2; exit 1; }
source_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
backup_dir=/var/lib/classic98-theme
install -d -m 755 "$backup_dir" /usr/share/plymouth/themes/classic98
if [[ ! -e $backup_dir/plymouthd.conf ]]; then
  cp -a /etc/plymouth/plymouthd.conf "$backup_dir/plymouthd.conf"
fi
for file in classic98.plymouth classic98.script unlock.png boot.png shutdown.png bullet.png progress.png preview-unlock.png; do
  install -m 644 "$source_dir/$file" "/usr/share/plymouth/themes/classic98/$file"
done
plymouth-set-default-theme classic98
if ! limine-mkinitcpio; then
  cp -a "$backup_dir/plymouthd.conf" /etc/plymouth/plymouthd.conf
  echo 'Build failed; restored the previous Plymouth theme configuration.' >&2
  exit 1
fi
echo 'Classic98 boot and shutdown theme installed. It will appear at next boot/shutdown.'
