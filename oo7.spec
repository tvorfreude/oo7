Name:           oo7
Version:        main
Release:        1%{?dist}
Summary:        Secret Service provider and alternative DBus secret portal backend

License:        MIT
URL:            https://github.com/linux-credentials/oo7
Source0:        %{url}/archive/main/%{name}-main.tar.gz

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(systemd)
BuildRequires:  pam-devel

%description
James Bond went on a new mission, and this time as a Secret Service provider.
oo7 is a modern collection of services and libraries centered around managing 
secrets securely, featuring a Rust-based implementation of the Secret portal 
and Secret Service specification.

%package -n git-credential-oo7
Summary:        Git credential helper replacement for git-credential-libsecret
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description -n git-credential-oo7
A git credential helper component derived from the oo7 suite designed to safely 
manage credentials via sandboxed Secret Service communication.

%prep
%autosetup -n %{name}-main

%build
# Build core rust workspaces 
cargo build --release %{?_smp_mflags}

# Build the portal component using Meson as structured in upstream
cd portal
%meson
%meson_build
cd ..

%install
# 1. Create the system binary directory
install -d %{buildroot}%{_bindir}

# 2. Install the compiled binaries manually from the target directory
install -p -m 0755 target/release/oo7-daemon %{buildroot}%{_bindir}/oo7-daemon
install -p -m 0755 target/release/git-credential-oo7 %{buildroot}%{_bindir}/git-credential-oo7

# 3. Use Meson to automatically discover, build, and deploy all configuration files
cd portal
%meson_install
cd ..

# 4. Check if Meson didn't catch the service configuration files. 
# If it skipped them, look for them dynamically in the project root:
if [ ! -f %{buildroot}%{_userunitdir}/oo7-daemon.service ]; then
    install -d %{buildroot}%{_userunitdir}
    find . -name "oo7-daemon.service" -exec cp {} %{buildroot}%{_userunitdir}/ \;
    find . -name "oo7-daemon.socket" -exec cp {} %{buildroot}%{_userunitdir}/ \;
fi


%files
%license LICENSE
%doc README.md
%{_bindir}/oo7-daemon
%{_libexecdir}/oo7-portal
%{_datadir}/applications/oo7-portal.desktop
%{_datadir}/xdg-desktop-portal/portals/oo7-portal.portal
%{_datadir}/dbus-1/services/org.freedesktop.impl.portal.desktop.oo7.service
%{_userunitdir}/oo7-daemon.service
%{_userunitdir}/oo7-daemon.socket
%{_userunitdir}/oo7-portal.service
%{_userunitdir}/dbus-org.freedesktop.impl.portal.desktop.oo7.service

%files -n git-credential-oo7
%{_bindir}/git-credential-oo7

%changelog
* Sat Aug 29 2026 Your Name <your-email@example.com> - 0.3.0-1
- Initial RPM packaging build implementation for Fedora Copr tracker
