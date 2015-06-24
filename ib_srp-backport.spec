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
Version:	2.0.33
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
Backport of the Linux IB/SRP 4.0 kernel module to earlier kernel versions.

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
* Wed Jun 24 2015 Bart Van Assche <bart.vanassche@sandisk.com> - 2.0.33
- rpmbuild: Suppress an rpmbuild warning.
- Makefile: Leave out a superfluous regular expression.
* Thu Apr 09 2015 Bart Van Assche <bart.vanassche@sandisk.com> - 2.0.32
- IB/srp: Port to Linux kernel 3.18/3.19/4.0.
- IB/srp: Cache subnet timeout.
- IB/srp: Improve the reconnect code.
- IB/srp: Convert three kzalloc() calls into kcalloc() calls.
- IB/srp: Add 64-bit LUN support.
- IB/srp: Restore target->comp_vector.
- IB/srp: Avoid SCSI host removal before scsi_create_target() returns.
- IB/srp: Change orig_dgid data type into ib_gid.
- IB/srp: Fix a printk format specifier.
- IB/srp: Align read-only variables properly.
- IB/srp: Change type of first argument of srp_init_ib_qp().
- IB/srp: Remove superfluous casts.
- IB/srp: Rename srp_connect_target() into srp_connect_ch().
- IB/srp: Add description for ch_count kernel module parameter.
- IB/srp: Rework pr_fmt() definition.
- IB/srp: Fix coding style.
- IB/srp: Add two comments.
- IB/srp: Adjust blank lines.
- IB/srp: Convert between spaces and tabs.
- scsi_transport_srp: Reduce failover time.
- scsi_transport_srp: Move two function definitions.
- scsi_transport_srp: Remove two superfluous forward declarations.
* Thu Apr 02 2015 Bart Van Assche <bart.vanassche@sandisk.com> - 2.0.31
- IB/srp: Fixed a sporadic crash during login on NUMA systems.
* Thu Mar 05 2015 Bart Van Assche <bart.vanassche@sandisk.com> - 2.0.30
- IB/srp: Suppress a false positive warning by srp_destroy_qp().
- IB/srp: Simplify building against (M)OFED kernel headers.
- IB/srp: Embed OFED flavor name in ib_srp kernel module version string.
- IB/srp: Fix build against SLES 11 + (M)OFED.
* Thu Jan 29 2015 Bart Van Assche <bart.vanassche@sandisk.com> - 2.0.29
- IB/srp: Use fast registration (FR) by default on UEK.
- Avoid that a SCSI rescan shortly after a cable pull sporadically triggers
  a kernel oops.
* Mon Oct 27 2014 Bart Van Assche <bart.vanassche@sandisk.com> - 2.0.28
- Fix a race condition triggered by destroying a queue pair.
- Increase default value of ch_count to a value above one.
- Add ch_count sysfs attribute.
- Allow newline separator for connection string.
- Use MODULE_VERSION().
* Tue Sep 30 2014 Bart Van Assche <bart.vanassche@sandisk.com> - 2.0.27
- Avoid that invoking srp_reset_host() after scsi_remove_host() causes
  trouble.
- Avoid that I/O hangs due to a cable pull during LUN scanning. Note: so
  far I have observed this hang only with multichannel support enabled
  (ch_count > 1).
- Fix a return value check in srp_init_module()
* Thu Jul 10 2014 Bart Van Assche <bvanassche@fusionio.com> - 2.0.26
- Fix endianness of immediate data offset field.
- Enable immediate data support by default.
- Fix SCSI residual handling.
- Fix a regression that got introduced via the multichannel code - avoid
  that NULL host_scribble can result in a kernel crash.
* Fri Jun 13 2014 Bart Van Assche <bvanassche@fusionio.com> - 2.0.25
- Added support for immediate data. This change improves write IOPS for
  small block sizes. This is a protocol change which is only enabled if
  the target system supports this.
- Made the CM timeout dependent on the subnet timeout. This reduces the
  failover time if the subnet timeout on the switch is below the default
  value (the default value of the subnet_timeout parameter is 18 for
  OpenSM).
- Fixed a deadlock that could be triggered by a cable pull.
- Added multichannel support. Multichannel support is disabled unless
  the ch_count kernel module parameter is set to another value than one.
- Added RDMA/CM support. This makes it possible to use the SRP initiator
  on Ethernet networks with a HCA that either supports RoCE or iWARP.
- Use the P_Key cache for P_Key lookups.
- Fixed a RHEL 7 build error.
- Display the name of the OFED flavor when building on a system on which
  either the OpenFabrics or the Mellanox OFED distribution has been
  installed.
- Added support for building the ib_srp-backport driver against Mellanox
  OFED installed with --add-kernel-support.
* Wed May 21 2014 Bart Van Assche <bvanassche@fusionio.com> - 2.0.24
- Builds again on 32-bit systems ("undefined reference to __udivdi3").
- Restored support for HCA\'s that neither support FMR nor FR.
- Fixed a (theoretical ?) memory registration failure that was
  introduced in Linux kernel v2.6.39 (state->npages being compared
  against SRP_FMR_SIZE instead of max_pages_per_fmr).
- Fixed fast_io_fail_tmo=dev_loss_tmo=off behavior.
- Simplified memory registration pool reallocation code in
  srp_create_target_ib(). If FMR or FR is supported, an memory
  registration pool is allocated. If this fails, an error code is
  returned. If neither FMR nor FR is supported no attempt is made to
  allocate a memory registration pool.
* Mon May 19 2014 Bart Van Assche <bvanassche@fusionio.com> - 2.0.23
- [FMR] Improved scalability by changing FMR support from one FMR pool per
  HCA into one FMR pool per SRP target connection. The FMR pool size has
  been reduced from 1024 to the SCSI host queue size. This change reduces
  memory consumption if the number of connections is small and improves
  performance if multiple SRP paths are used.
- The maximum number of pages per memory registration pool is now derived
  from the HCA device attributes instead of using a loop that iterates until
  a supported size is found.
- The SCSI host queue size (/sys/class/scsi_host/host*/can_queue) is
  decreased dynamically in the (unlikely) case where the number of memory
  descriptors is exhausted. This scenario can only be triggered with
  fragmented SG_IO requests and a high queue depth. Neither fio nor the
  Linux page cache can generate such a workload.
- Fixed a sporadic crash triggered by cable pulling. See also
  http://thread.gmane.org/gmane.linux.drivers.rdma/19068/focus=19069 for
  more information.
- [FR] An error message is logged and the connection is reestablished if a
  "local invalidation" work request fails.
- [FR] Renamed the kernel module parameter "prefer_frwr" into "prefer_fr"
  (FR = fast registration).
- Reworked the code in the Makefile for detecting the OFED version.
* Tue Mar 25 2014 Bart Van Assche <bvanassche@fusionio.com> - 2.0.22
- Reworked FRWR support (FRWR = fast registration work request; an alternative
  for FMR to register memory with an HCA). Added support for non-contiguous
  memory regions. One FRWR pool per connection instead of one per initiator
  HCA to maximize scalability. Removed the "fast_reg" sysfs attribute and the
  "use_fast_reg" login parameter since the choice between FRWR and FMR is now
  global instead of per SRP connection. Added the "register_always" kernel
  module parameter to make it easier to test the FRWR implementation.
* Mon Mar 17 2014 Bart Van Assche <bvanassche@fusionio.com> - 2.0.21
- Fixed a small performance regression that got introduced in v2.0.20.
* Thu Mar 6 2014 Bart Van Assche <bvanassche@fusionio.com> - 2.0.20
- Fixed a hard to trigger race condition that could be hit when the
  fast_io_fail_tmo timer expires and that could result in a kernel crash.
- Fixed a hard to trigger race condition that could be hit on RHEL 6
  initiator systems when the reconnect_delay timer expires and that could
  result in a kernel crash.
- Build fix for SLES 11 SP3.
* Fri Feb 21 2014 Bart Van Assche <bvanassche@fusionio.com> - 2.0.19
- Reduced the default value of the tl_retry_count parameter from 3 into 2.
  This change reduces the time needed to detect a cable pull from about
  17s to about 13s.
- SGID and DGID are now included in LOGIN REJECTED messages. SGID is now
  included in new target messages. This makes it possible to determine
  which IB ports these messages apply to.
- Fixed the description of the dev_loss_tmo kernel module parameter.
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
* Mon Nov 25 2013 Bart Van Assche <bvanassche@fusionio.com> - 2.0.14
- FRWR mode: avoid that paths start to bounce after a cable reconnect.
- Fixed a regression introduced in v2.0.13 that sometimes caused multipathd
  to stall for two minutes.
* Mon Nov 25 2013 Bart Van Assche <bvanassche@fusionio.com> - 2.0.13
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
* Sun Sep 08 2013 Bart Van Assche <bvanassche@fusionio.com> - 2.0.4
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
