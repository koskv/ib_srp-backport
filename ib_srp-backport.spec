%define kmod_name ib_srp-backport

Name:		%{kmod_name}-%{kversion}
Version:	2.0.5
Release:	1
Summary:	%{kmod_name} kernel modules
Group:		System/Kernel
License:	GPLv2
URL:		http://www.fusionio.com/
BuildRequires:	gcc make
Source:		%{kmod_name}-%{version}.tar.bz2
AutoReq:	0
Requires:	/sbin/depmod /usr/bin/find %{kernel_rpm}
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-build-%(%{__id_u} -n)

%description
Backport of the Linux IB/SRP 3.11 kernel module to earlier kernel versions.

%prep
rm -rf $RPM_BUILD_ROOT

%setup -q -n %{kmod_name}-%{version}

%build
KVER=%{kversion} make

%install
export INSTALL_MOD_PATH=$RPM_BUILD_ROOT
export INSTALL_MOD_DIR=extra/%{kmod_name}
KVER=%{kversion} make install
# Clean up unnecessary kernel-generated module dependency files.
find $INSTALL_MOD_PATH/lib/modules -iname 'modules.*' -exec rm {} \;

%clean
rm -rf $RPM_BUILD_ROOT

%pre
modprobe -r ib_srp
modprobe -r scsi_transport_srp
find /lib/modules/%{kversion} -name ib_srp.ko -o -name scsi_transport_srp.ko \
    | while read f; do rm -f "$f"; done

%post
depmod %{kversion}

%files
/lib/modules/%{kversion}/extra/%{kmod_name}/*.ko

%changelog
* Fri Sep 13 2013 Bart Van Assche <bvanassche@fusionio.com> - 2.0.5
- Fixed three bugs in the FRWR code: handle non-aligned SG_IO buffers properly;
  avoid triggering an infinite loop if mapping fails; tell the SCSI mid-layer
  what the maximum number of sectors is that is supported in FRWR mode.
- Added prefer_frwr kernel module parameter (default value false aka use FMR).
- Fix a race condition between the code for time-based reconnecting and the
  SCSI EH.
* Sun Sep 09 2013 Bart Van Assche <bvanassche@fusionio.com> - 2.0.4
- The RPM depends now on /boot/vmlinuz-\${kv} instead of /lib/modules/\${kv}.
* Sun Sep 08 2013 Bart Van Assche <bvanassche@fusionio.com> - 2.0.3
- Since IB symbols are not in the KABI, make this RPM dependent on the kernel
  RPM it has been built against.
* Mon Sep 02 2013 Bart Van Assche <bvanassche@fusionio.com> - 2.0.2
- Avoid offlining operational SCSI devices
* Wed Aug 28 2013 Bart Van Assche <bvanassche@fusionio.com> - 2.0.1
- Enlarged IB send queue size when using FRWR.
* Thu Aug 22 2013 Bart Van Assche <bvanassche@fusionio.com> - 2.0.0
- Created this package.
