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

/* <linux/printk.h> */
#ifndef pr_warn
#define pr_warn pr_warning
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

#endif
