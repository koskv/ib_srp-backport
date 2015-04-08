#include <scsi/scsi_host.h>

static int cqd(struct scsi_device *sdev, int qdepth, int reason)
{
	return 0;
}

static int modinit(void)
{
	struct scsi_host_template t = { .change_queue_depth = cqd };

	return t.change_queue_depth(NULL, 0, 0);
}

module_init(modinit);
