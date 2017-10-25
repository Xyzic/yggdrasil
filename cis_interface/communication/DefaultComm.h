#include <CommBase.h>

/*! @brief Flag for checking if this header has already been included. */
#ifndef CISDEFAULTCOMM_H_
#define CISDEFAULTCOMM_H_

#define IPCDEF

// IPC Comm
#ifdef IPCDEF
#include <IPCComm.h>
comm_type _default_comm = IPC_COMM;
#define new_default_address new_ipc_address
#define init_default_comm init_ipc_comm
#define free_default_comm free_ipc_comm
#define default_comm_nmsg ipc_comm_nmsg
#define default_comm_send ipc_comm_send
#define default_comm_recv ipc_comm_recv
// ZMQ Comm
#else
#include <ZMQComm.h>
comm_type _default_comm = ZMQ_COMM;
#define new_default_address new_zmq_address
#define init_default_comm init_zmq_comm
#define free_default_comm free_zmq_comm
#define default_comm_nmsg zmq_comm_nmsg
#define default_comm_send zmq_comm_send
#define default_comm_recv zmq_comm_recv
#endif

#endif /*CISDEFAULTCOMM_H_*/
