# Classic98 boot and shutdown dialogs

The boot password prompt on this machine is Plymouth's encrypted-disk unlock prompt. SDDM automatically logs in afterward. This theme changes Plymouth presentation only; it retains Plymouth's password, text question, progress, and message callbacks. It does not change disk encryption, PAM, or autologin.

Silver raised dialog, blue gradient caption, white inset password field, black password dots, and segmented navy progress on a solid teal background. Text is rendered into the assets using the installed Microsoft Sans Serif, so no font file is needed in the initramfs.

`python build-assets.py` regenerates assets and three composited previews. `pkexec ./install.sh` installs a separate `/usr/share/plymouth/themes/classic98` theme and runs `limine-mkinitcpio`. This is a system-wide choice, independent of desktop theme switching. No packaged Omarchy files are modified. The old Plymouth configuration is saved at `/var/lib/classic98-theme/plymouthd.conf`.

Restore with `sudo cp /var/lib/classic98-theme/plymouthd.conf /etc/plymouth/plymouthd.conf` followed by `sudo limine-mkinitcpio`.

The installed Plymouth script parser validates `classic98.script`. The previews are composited illustrations, not live boot screenshots; actual boot, password failure messages, and shutdown must be verified at the next reboot.
