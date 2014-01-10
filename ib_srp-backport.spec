%define kmod_name ib_srp-backport
%define kversion %{expand:%%(echo ${KVER:-$(uname -r)})}
%define kernel_rpm %{expand:%%(						\
          krpm="$(rpm -qf /boot/vmlinuz-%{kversion} 2>/dev/null |	\
                grep -v 'is not owned by any package' | head -n 1)";	\
          if [ -n "$krpm" ]; then					\
            echo "/boot/vmlinuz-%{kversion}";				\
          else								\
            echo "%{nil}";						\
          fi;								\
	)}

Name:		%{kmod_name}-%{kversion}
Version:	2.0.18
Release:	1
Summary:	%{kmod_name} kernel modules
Group:		System/Kernel
License:	GPLv2
URL:		http://www.fusionio.com/
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
for m in ib_srp scsi_transport_srp; do
    if [ -d /sys/module/$m ]; then
	rmmod $m
    fi
done
find /lib/modules/%{kversion} -name ib_srp.ko -o -name scsi_transport_srp.ko \
    | while read f; do rm -f "$f"; done

%post
depmod %{kversion}

%preun
for m in ib_srp scsi_transport_srp; do
    if [ -d /sys/module/$m ]; then
	rmmod $m
    fi
done

%postun
depmod %{kversion}

%files
/lib/modules/%{kversion}/extra/%{kmod_name}/*.ko

%changelog
* Fri Jan 10 2014 Bart Van Assche <bvanassche@fusionio.com> - 2.0.18
- Build fix for RHEL 6.5 (kernel headers >= 2.6.32-431.3.1.el6)
- Build fix for RHEL 5.x for a change introduced in v2.0.15 of this driver.
* Mon Jan 06 2014 Bart Van Assche <bvanassche@fusionio.com> - 2.0.17
- Log initiator and target GID if a login has been rejected. An example:
  kernel: scsi host11: ib_srp: SRP LOGIN from fe80:0000:0000:0000:0002:c903:00a3:4fb1 to fe80:0000:0000:0000:0002:c903:00a3:4271 REJECTED, reason 0x00010001
* Thu Dec 19 2013 Bart Van Assche <bvanassche@fusionio.com> - 2.0.16
- Avoid that the process that writes into the sysfs attribute "add_target"
  hangs if a transport layer error occurs after the SRP login request has
  been sent and before the SRP login reponse has been received.
* Mon Dec 16 2013 Bart Van Assche <bvanassche@fusionio.com> - 2.0.15
- Fail SCSI commands silently that failed because of a transport layer
  error.
* Mon Nov 26 2013 Bart Van Assche <bvanassche@fusionio.com> - 2.0.14
- FRWR mode: avoid that paths start to bounce after a cable reconnect.
- Fixed a regression introduced in v2.0.13 that sometimes caused multipathd
  to stall for two minutes.
* Mon Nov 26 2013 Bart Van Assche <bvanassche@fusionio.com> - 2.0.13
- Fix a sporadic kernel crash triggered by path failover.
- Renamed can_queue login parameter into queue_size.
* Mon Nov 18 2013 Bart Van Assche <bvanassche@fusionio.com> - 2.0.12
- Block the SCSI devices upon TL error also if fast_io_fail_tmo = off.
* Mon Nov 04 2013 Bart Van Assche <bvanassche@fusionio.com> - 2.0.11
- Made it possible to rebuild the source RPM.
* Tue Oct 29 2013 Bart Van Assche <bvanassche@fusionio.com> - 2.0.10
- Avoid that the initiator logs in twice to the same target port if the
  same login string is written into the add_target sysfs attribute from
  two different threads.
- Avoid that failback can fail with reconnect_delay = fast_io_fail_tmo.
* Wed Oct 02 2013 Bart Van Assche <bvanassche@fusionio.com> - 2.0.9
- Avoid that if reconnecting succeeds and the SCSI error handler later
  on invokes eh_host_reset_handler that paths remain in the fail-fast
  state and hence that failback fails.
* Fri Sep 27 2013 Bart Van Assche <bvanassche@fusionio.com> - 2.0.8
- Avoid blocking commands for dev_loss_tmo seconds if reconnecting fails.
- Reduce fail-over time.
* Tue Sep 24 2013 Bart Van Assche <bvanassche@fusionio.com> - 2.0.7
- Changed default value of reconnect_delay from 10s into 20s.
- Export source port GID (sgid) to sysfs.
- Make srp_remove_host() terminate I/O.
- Fixed sporadic I/O hang due to cable pull.
- Fixed use-after-free triggered by cable pull or driver unload.
- Added %%preun and %%postun sections in the spec file.
* Fri Sep 13 2013 Bart Van Assche <bvanassche@fusionio.com> - 2.0.6
- Made FRWR mapping code detect discontiguous buffers correctly.
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
