#include <scsi/scsi_host.h>

static int modinit(void)
{
	struct scsi_host_template t = { .track_queue_depth = 1 };

	return 0;
}

module_init(modinit);
