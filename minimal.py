import pathlib
import shlex
import subprocess

def run_command(command: str) -> None:
    print('Running:', command)
    command = shlex.split(command)
    return
    print(subprocess.check_output(command))

def disable_service(name):
    run_command('systemctl disable ' + name)

def append_to_file(path: str, *content: list[str]) -> None:
    print(f'Writing to file {path}:')
    print('\n'.join(content))
    return
    path = pathlib.Path(path)
    path.parent.mkdir(exist_ok=True)
    with open(path, 'a') as f:
        f.writelines(content)

def ask(question: str) -> bool:
    print()
    response = input(question + ' [y/N] ')
    if response.strip() in ('y', 'Y'):
        return True
    return False

if __name__ == '__main__':
    if ask('Disable coredump to save disk space?'):
        append_to_file(
            '/etc/systemd/coredump.conf.d/coredump.conf',
            '[Coredump]',
            'Storage=none',
        )
    if ask('Reduce journal size to 10MB and level to INFO to save disk space?'):
        append_to_file(
            '/etc/systemd/journald.conf.d/journald.conf',
            '[Journal]',
            'SystemMaxUse=10M',
            'SystemMaxFileSize=1M',
            'MaxLevelStore=info',
            'Audit=off',
        )
    if ask('Tune TCP and VM for lower latency?'):
        append_to_file(
            '/etc/sysctl.d/99-sysctl.conf',
            'net.ipv4.tcp_slow_start_after_idle = 0',
            'net.ipv4.tcp_fastopen = 3',
            'net.ipv4.tcp_fin_timeout = 10',
            'net.ipv4.tcp_low_latency = 1',
            'vm.dirty_background_ratio = 2',
        )
    if ask('Want faster bootup?'):
        disable_service('NetworkManager-wait-online.service')

    if ask('Remove abrt, anaconda, avahi, dnf-makecache, firewalld, fprintd, geoclue, ibus-typing-booster, pcsc-lite?'):
        disable_service('dnf-makecache.timer')
        disable_service('firewalld')
        run_command('dnf remove -y abrt anaconda avahi fprintd geoclue ibus-typing-booster pcsc-lite')

    if ask('Remove openvpn?'):
        run_command('dnf remove -y openvpn')

    if ask('Disable flatpak, PackageKit, podman?'):
        run_command('dnf remove -y flatpak PackageKit podman')

    if ask('Is the system without a printer or a scanner?'):
        run_command('dnf remove -y cups simple-scan')

    if ask('Is LVM unused?'):
        # disable_service('lvm2-monitor.service')
        run_command('dnf remove -y lvm2')

    if ask('Is RAID unused?'):
        disable_service('mdmonitor.service')
        disable_service('raid-check.service')
        run_command('dnf remove -y dmraid')

    if ask('Is remote login (sssd) unused?'):
        run_command('dnf remove -y sssd sssd-kcm')

    if ask('Is the system without nVidia graphics?'):
        disable_service('switcheroo-control.service')
        run_command('dnf remove -y nvidia-gpu-firmware')

    if ask('Is the system without AMD graphics?'):
        run_command('dnf remove -y amd-gpu-firmware')

    if ask('Is the system without a modem?'):
        disable_service('ModemManager.service')

    if ask('Disable SELinux, hardened usercopy, watchdog for better performance?'):
        disable_service('selinux-autorelabel-mark.service')
        run_command('dnf remove -y audit')
        run_command('grubby --update-kernel=ALL --args="selinux=0 audit=0 hardened_usercopy=off nowatchdog"')

    if ask('Remove unnecessary GNOME apps?'):
        run_command('dnf remove -y '
                    'gnome-abrt '
                    'gnome-backgrounds '
                    'gnome-boxes '
                    'gnome-connections '
                    'gnome-contacts '
                    'gnome-maps '
                    'gnome-photos '
                    'gnome-remote-desktop '
                    'gnome-shell-extension-apps-menu '
                    'gnome-shell-extension-background-logo '
                    'gnome-shell-extension-places-menu '
                    'gnome-shell-extension-window-list '
                    'gnome-session-xsession '
                    'gnome-software '
                    'gnome-tour '
                    'gnome-user-docs '
                    'gnome-user-share '
                    'gnome-video-effects '
                    'gnome-weather '
                    'mediawriter '
                    'rhythmbox '
                    'yelp ')

    if ask('Remove Firefox and LibreOffice?'):
        run_command('dnf remove -y firefox libreoffice-core')

    if ask('Install useful desktop utilities?'):
        run_command('dnf install -y '
                    'gnome-console '
                    'gnome-extensions-app '
                    'gnome-shell-extension-dash-to-panel '
                    'gnome-tweaks '
                    'lsd ')
        run_command('dnf remove -y gnome-terminal')

    if ask('Do final clean up?'):
        run_command('rm -r /var/cache/PackageKit')
        run_command('sudo rm -r /var/lib/systemd/coredump')
        run_command('sudo dnf clean all')
        run_command('sudo journalctl --rotate')
        run_command('sudo journalctl --vacuum-files=1')