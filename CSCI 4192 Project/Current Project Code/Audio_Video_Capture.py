import time
import os
import subprocess
import signal


# ================= CONFIG =================
PCAP_OUTPUT_FILE = "/home/sadik/Downloads/PluggableTransportCaptures/Non_Tor_Audio_Call_Capture.pcapng" # For Tor, change to Tor_<Pluggable Transport>_Audio_Call_Capture.pcapng
INTERFACE = "enp0s3"  # For Tor, change to enp0s8
CAPTURE_LENGTH = 60 * 60 * 4


# ============================================================
#           PRIVILEGE + NIC OFFLOAD HELPERS (NEW)
# ============================================================
def is_root() -> bool:
    return os.geteuid() == 0


def run_root_cmd(cmd: list, check: bool = True):
    """
    Run a command as root. If not root, it will use sudo.
    """
    if is_root():
        return subprocess.run(cmd, check=check)
    else:
        return subprocess.run(["sudo"] + cmd, check=check)


def disable_nic_offloads(interface: str):
    """
    Disable common NIC offloads to avoid capture distortions.
    """
    print(f"Disabling NIC offloads on {interface} ...")
    cmd = [
        "ethtool", "-K", interface,
        "gro", "off",
        "gso", "off",
        "tso", "off",
        "lro", "off",
        "tx", "off",
        "rx", "off",
    ]
    run_root_cmd(cmd, check=True)
    print("NIC offloads disabled.")


# =======================
# TShark Start/Stop
# =======================
def start_tshark_capture():
    print("📡 Starting tshark capture...")
    cmd = ["tshark", "-i", INTERFACE, "-w", PCAP_OUTPUT_FILE, "-q"]
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def stop_tshark(process):
    print("Stopping tshark capture...")
    process.send_signal(signal.SIGINT)
    process.wait()
    print(f" Traffic capture saved to: {PCAP_OUTPUT_FILE}")


if __name__ == '__main__':
    # Disable NIC offloads BEFORE starting tshark
    disable_nic_offloads(INTERFACE)

    tshark_proc = start_tshark_capture()
    time.sleep(5)  # Let tshark initialize

    # Sleep for 4 hours and allow audio/video transfer to take place
    time.sleep(CAPTURE_LENGTH)

    stop_tshark(tshark_proc)
