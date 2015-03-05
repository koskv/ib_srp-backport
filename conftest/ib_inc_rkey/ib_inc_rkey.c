#include <linux/module.h>
#include <rdma/ib_verbs.h>

static int modinit(void)
{
	return ib_inc_rkey(0);
}

module_init(modinit);
