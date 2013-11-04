#
# Makefile for scsi_transport_srp.ko and ib_srp.ko.
#

ifeq ($(KVER),)
  ifeq ($(KDIR),)
    KVER = $(shell uname -r)
    KDIR ?= /lib/modules/$(KVER)/build
  else
    KVER = $$KERNELRELEASE
  endif
else
  KDIR ?= /lib/modules/$(KVER)/build
endif

VERSION := $(shell sed -n 's/Version:[[:blank:]]*//p' ib_srp-backport.spec)

# The file Modules.symvers has been renamed in the 2.6.18 kernel to
# Module.symvers. Find out which name to use by looking in $(KDIR).
MODULE_SYMVERS:=$(shell if [ -e $(KDIR)/Module.symvers ]; then \
		       echo Module.symvers; else echo Modules.symvers; fi)

# Whether or not the OFED kernel modules have been installed.
OFED_KERNEL_IB_RPM:=$(shell for r in kernel-ib mlnx-ofa_kernel compat-rdma; do rpm -q $$r 2>/dev/null | grep -q $$(uname -r | sed 's/-/_/g') && echo $$r; done)

# Whether or not the OFED kernel-ib-devel RPM has been installed.
OFED_KERNEL_IB_DEVEL_RPM:=$(shell for r in kernel-ib-devel mlnx-ofa_kernel-devel compat-rdma-devel; do rpm -q $$r 2>/dev/null | grep -q $$(uname -r | sed 's/-/_/g') && echo $$r; done)

OFED_KERNEL_DIR:=$(shell if rpm -q compat-rdma-devel >/dev/null 2>&1; then \
			     echo /usr/src/compat-rdma;			   \
			 elif rpm -q kernel-ib-devel >/dev/null 2>&1; then \
			     echo /usr/src/ofa_kernel;			   \
			 elif rpm -q mlnx-ofa_kernel-devel >/dev/null 2>&1;\
			     then					   \
			     echo /usr/src/ofa_kernel;			   \
			 fi)

ifneq ($(OFED_KERNEL_IB_DEVEL_RPM),)
# Read OFED's config.mk, which contains the definition of the variable
# BACKPORT_INCLUDES.
include $(OFED_KERNEL_DIR)/config.mk
OFED_CFLAGS:=$(BACKPORT_INCLUDES) -I$(OFED_KERNEL_DIR)/include
OFED_MODULE_SYMVERS:=$(OFED_KERNEL_DIR)/Module.symvers
endif

INSTALL_MOD_DIR ?= extra

all: check
	CONFIG_SCSI_SRP_ATTRS=m						   \
		$(MAKE) -C $(KDIR) M=$(shell pwd)/drivers/scsi		   \
		PRE_CFLAGS="$(OFED_CFLAGS)" modules
	@m="$(shell pwd)/drivers/infiniband/ulp/srp/$(MODULE_SYMVERS)";	   \
	cat <"$(KDIR)/$(MODULE_SYMVERS)" >"$$m";			   \
	cat "$(shell pwd)/drivers/scsi/$(MODULE_SYMVERS)"		   \
		$(OFED_MODULE_SYMVERS) |				   \
	while read line; do						   \
	    set -- $$line;						   \
	    csum="$$1";							   \
	    sym="$$2";							   \
	    if ! grep -q "^$$csum[[:blank:]]*$$sym[[:blank:]]" "$$m"; then \
		sed -i.tmp -e "/^[\w]*[[:blank:]]*$$sym[[:blank:]]/d" "$$m"; \
		echo "$$line" >>"$$m";					   \
	    fi								   \
	done
	$(MAKE) -C $(KDIR) M=$(shell pwd)/drivers/infiniband/ulp/srp	   \
	    PRE_CFLAGS="$(OFED_CFLAGS)" modules

install: all
	install -vD -m 644 drivers/scsi/scsi_transport_srp.ko  \
	$(INSTALL_MOD_PATH)/lib/modules/$(KVER)/$(INSTALL_MOD_DIR)/scsi_transport_srp.ko
	install -vD -m 644 drivers/infiniband/ulp/srp/ib_srp.ko \
	$(INSTALL_MOD_PATH)/lib/modules/$(KVER)/$(INSTALL_MOD_DIR)/ib_srp.ko
	if [ -z "$(INSTALL_MOD_PATH)" ]; then	\
	  /sbin/depmod -a $(KVER);			\
	fi

uninstall:
	rm -f $(INSTALL_MOD_PATH)/lib/modules/$(KVER)/$(INSTALL_MOD_DIR)/scsi_transport_srp.ko
	rm -f $(INSTALL_MOD_PATH)/lib/modules/$(KVER)/$(INSTALL_MOD_DIR)/ib_srp.ko
	if [ -z "$(INSTALL_MOD_PATH)" ]; then	\
	  /sbin/depmod -a $(KVER);			\
	fi

check:
	@if [ -n "$(OFED_KERNEL_IB_RPM)" ]; then                            \
	  if [ -z "$(OFED_KERNEL_IB_DEVEL_RPM)" ]; then                     \
	    echo "Error: the $(OFED_KERNEL_IB_RPM) development package has" \
	         "not yet been installed.";                                 \
	    false;                                                          \
	  elif [ -e /lib/modules/$(KVER)/kernel/drivers/infiniband ]; then  \
	    echo "Error: the distro-provided InfiniBand kernel drivers"     \
	         "must be removed first.";                                  \
	    false;                                                          \
	  elif [ -e /lib/modules/$(KVER)/updates/drivers/infiniband/ulp/srp/ib_srp.ko ]; then \
	    echo "Error: the OFED SRP initiator must be removed first"      \
                 "(/lib/modules/$(KVER)/updates/drivers/infiniband/ulp/srp/ib_srp.ko).";    \
	    false;                                                          \
	  elif [ -e $(KDIR)/scripts/Makefile.lib ]                          \
	       && ! grep -wq '^c_flags .*PRE_CFLAGS'                        \
                  $(KDIR)/scripts/Makefile.lib                              \
	       && ! grep -wq '^LINUXINCLUDE .*PRE_CFLAGS'                   \
                  $(KDIR)/Makefile; then                                    \
	    echo "Error: the kernel build system has not yet been patched.";\
	    false;                                                          \
	  else                                                              \
	    echo "  Building against OFED InfiniBand kernel headers.";      \
	  fi                                                                \
	else                                                                \
	  if [ -n "$(OFED_KERNEL_IB_DEVEL_RPM)" ]; then                     \
	    echo "Error: the OFED kernel RPM has not yet been installed.";  \
	    false;                                                          \
	  else                                                              \
	    echo "  Building against non-OFED InfiniBand kernel headers.";  \
	  fi;                                                               \
	fi

dist-gzip:
	mkdir ib_srp-backport-$(VERSION) &&		\
	{ git ls-tree --name-only -r HEAD	|	\
	  tar -T- -cf- |				\
	  tar -C ib_srp-backport-$(VERSION) -xf-; } &&	\
	rm -f ib_srp-backport-$(VERSION).tar.bz2 &&	\
	tar -cjf ib_srp-backport-$(VERSION).tar.bz2	\
		ib_srp-backport-$(VERSION) &&		\
	rm -rf ib_srp-backport-$(VERSION)

# Build an RPM either for the running kernel or for kernel version $KVER.
rpm:
	name=ib_srp-backport &&						 \
	rpmtopdir="$$(if [ $$(id -u) = 0 ]; then echo /usr/src/packages; \
		      else echo $$PWD/rpmbuilddir; fi)" &&		 \
	$(MAKE) dist-gzip &&						 \
	rm -rf $${rpmtopdir} &&						 \
	for d in BUILD RPMS SOURCES SPECS SRPMS; do			 \
	  mkdir -p $${rpmtopdir}/$$d;					 \
	done &&								 \
	cp $${name}-$(VERSION).tar.bz2 $${rpmtopdir}/SOURCES &&		 \
	rpmbuild --define="%_topdir $${rpmtopdir}"			 \
		 -ba $${name}.spec &&					 \
	rm -f ib_srp-backport-$(VERSION).tar.bz2

clean:
	$(MAKE) -C $(KDIR) M=$(shell pwd)/drivers/scsi clean
	$(MAKE) -C $(KDIR) M=$(shell pwd)/drivers/infiniband/ulp/srp clean
	rm -f Modules.symvers Module.symvers Module.markers modules.order

extraclean: clean
	rm -f *.orig *.rej

.PHONY: all check clean dist-gzip extraclean install rpm
