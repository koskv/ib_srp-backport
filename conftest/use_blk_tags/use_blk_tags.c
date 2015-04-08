#include <scsi/scsi_host.h>

static int modinit(void)
{
	struct scsi_host_template t = { .use_blk_tags = 1 };

	return 0;
}

module_init(modinit);
