#ifndef _LINUX_BACKPORT_H_
#define _LINUX_BACKPORT_H_

#include <stdarg.h>           /* va_list */
#include <linux/kernel.h>     /* asmlinkage */
#include <linux/types.h>      /* u32 */
#include <linux/version.h>    /* LINUX_VERSION_CODE */
#if LINUX_VERSION_CODE >= KERNEL_VERSION(2, 6, 37)
#include <linux/printk.h>     /* pr_warn() -- see also commit 968ab18 */
#endif
#include <scsi/scsi_device.h> /* SDEV_TRANSPORT_OFFLINE */

/* <linux/kernel.h> */
#if LINUX_VERSION_CODE < KERNEL_VERSION(2, 6, 39) &&  \
	(!defined(RHEL_MAJOR) || RHEL_MAJOR -0 < 6 || \
	 RHEL_MAJOR -0 == 6 && RHEL_MINOR -0 < 4)
static inline int __must_check kstrtouint(const char *s, unsigned int base,
					  unsigned int *res)
{
	unsigned long lres;
	int ret;

	ret = strict_strtoul(s, base, &lres);
	if (ret == 0)
		*res = lres;
	return ret;
}

static inline int __must_check kstrtoint(const char *s, unsigned int base,
					 int *res)
{
	long lres;
	int ret;

	ret = strict_strtol(s, base, &lres);
	if (ret == 0)
		*res = lres;
	return ret;
}
#endif

/* <linux/lockdep.h> */
#if LINUX_VERSION_CODE < KERNEL_VERSION(2, 6, 32)
#define lockdep_assert_held(lock) do { } while(0)
#endif

/* <linux/printk.h> */
#ifndef pr_warn
#define pr_warn pr_warning
#endif

/* <linux/scatterlist.h> */
#if LINUX_VERSION_CODE <= KERNEL_VERSION(2, 6, 18)
#define for_each_sg(sglist, sg, nr, __i)        \
	for (__i = 0, sg = (sglist); __i < (nr); __i++, (sg)++)
#endif

/* <linux/types.h> */
#if LINUX_VERSION_CODE <= KERNEL_VERSION(2, 6, 18)
typedef unsigned long uintptr_t;
#endif

/* <rdma/ib_verbs.h> */
/* commit 7083e42e */
#if LINUX_VERSION_CODE < KERNEL_VERSION(3, 9, 0)
/**
 * ib_inc_rkey - increments the key portion of the given rkey. Can be used
 * for calculating a new rkey for type 2 memory windows.
 * @rkey - the rkey to increment.
 */
static inline u32 ib_inc_rkey(u32 rkey)
{
	const u32 mask = 0x000000ff;
	return ((rkey + 1) & mask) | (rkey & ~mask);
}
#endif

/* <scsi/scsi.h> */
#if LINUX_VERSION_CODE < KERNEL_VERSION(2, 6, 35) && !defined(FAST_IO_FAIL)
/*
 * commit 2f2eb58 ([SCSI] Allow FC LLD to fast-fail scsi eh by introducing new
 * eh return)
 */
#define FAST_IO_FAIL FAILED
#endif
#if LINUX_VERSION_CODE <= KERNEL_VERSION(2, 6, 18)
#define SCSI_MAX_SG_CHAIN_SEGMENTS (PAGE_SIZE / sizeof(void*))
#endif

/* <scsi/scsi_device.h> */
/* See also commit 5d9fb5cc */
#if LINUX_VERSION_CODE < KERNEL_VERSION(3, 5, 0) && \
	!defined(SDEV_TRANSPORT_OFFLINE)
#define SDEV_TRANSPORT_OFFLINE SDEV_OFFLINE
#endif

static inline void scsi_target_unblock_compat(struct device *dev,
					      enum scsi_device_state new_state)
{
#if LINUX_VERSION_CODE < KERNEL_VERSION(3, 5, 0)
	scsi_target_unblock(dev);
#else
	scsi_target_unblock(dev, new_state);
#endif
}

#define scsi_target_unblock scsi_target_unblock_compat

/* <scsi/scsi_host.h> */
#if LINUX_VERSION_CODE >= KERNEL_VERSION(2, 6, 33) || \
	(defined(RHEL_MAJOR) && RHEL_MAJOR -0 >= 6)
#define HAVE_SCSI_QDEPTH_REASON
#else
/*
 * See also commit e881a172 (modify change_queue_depth to take in reason why it
 * is being called).
 */
enum {
	SCSI_QDEPTH_DEFAULT,	/* default requested change, e.g. from sysfs */
	SCSI_QDEPTH_QFULL,	/* scsi-ml requested due to queue full */
	SCSI_QDEPTH_RAMP_UP,	/* scsi-ml requested due to threshold event */
};
#endif

#endif
