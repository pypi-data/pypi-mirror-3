"""Majordomo Protocol definitions. """

# The version of MDP/Client that we implement.
C_CLIENT = "MDPC01"

# The version of MDP/Worker that we implement.
W_WORKER = "MDPW01"

# MDP/Server commands.
W_READY = "\001"
W_REQUEST = "\002"
W_REPLY = "\003"
W_HEARTBEAT = "\004"
W_DISCONNECT = "\005"

commands = [None, "READY", "REQUEST", "REPLY", "HEARTBEAT", "DISCONNECT"]
