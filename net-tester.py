# implement an iperf client in Python using sockets

import socket
import time
import threading
import argparse
import sys
from typing import Optional
import select
import csv

""""
    Usage
    -----
    - Instantiate with an optional CSV file path. Use none to disable, or a path
      like "results.csv" to enable CSV output. By default the class output performance results to "results.csv".
    - Call log_stat() to record individual measurements.
    - Call summary() to print aggregated statistics.
    - Call close() to close any open CSV resource before program exit.

    Example
    -------
    logger = Logger("out.csv")
    logger.log_info("Starting test")
    logger.log_stat(time.time(), "192.0.2.1", 5201, bandwidth=12.34)
    logger.summary()
    logger.close()
"""


class Logger:
    """
    Logger
    ------
    Logger class for recording and displaying network test metrics"""

    INFO = '\033[94m[INFO]\033[0m '
    ERROR = '\033[91m[ERROR]\033[0m '

    class Stat:
        """A class to model a single measurement record"""

        def __init__(self, timestamp: float, bandwidth: Optional[float] = None,
                     loss: Optional[float] = None, jitter: Optional[float] = None):
            self.timestamp = timestamp
            self.bandwidth = bandwidth
            self.loss = loss
            self.jitter = jitter

    def __init__(self, csv_output: Optional[str] = "results.csv"):
        """Initialize Logger with optional CSV output"""
        self.stats: List[Logger.Stat] = []  # List to store measurements
        self.csv_output = csv_output        # CSV file path or None
        self.csv_file = None               # File handle for CSV
        self.csv_writer = None             # CSV writer object

        # If the csv parameter is None, then disable CSV output
        if csv_output:
            self.csv_file = open(csv_output, 'w', newline='')
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow(
                ['timestamp', 'elapsed', 'bandwidth_mbps', 'loss_percent', 'jitter_ms'])

    def log_stat(self, timestamp: float, ip: str, port: int, bandwidth: Optional[float] = None,
                 loss: Optional[float] = None, jitter: Optional[float] = None) -> None:
        """
        Log a measurement (all parameters optional)
        - timestamp: Time of measurement (float)
        - ip: Client IP address (str)
        - port: Client port number (int)
        - bandwidth: Bandwidth in Mbps (float, optional)
        - loss: Packet loss in percent (float, optional)
        - jitter: Jitter in milliseconds (float, optional)
        """
        stat = Logger.Stat(timestamp, bandwidth, loss, jitter)
        self.stats.append(stat)
        elapsed = 0.0
        if len(self.stats) > 1:
            elapsed = timestamp - self.stats[0].timestamp

        # Write to CSV if enabled
        if self.csv_writer:
            self.csv_writer.writerow([
                ip, port,
                timestamp,
                f"{elapsed:.3f}",
                f"{bandwidth:.2f}" if bandwidth is not None else "",
                f"{loss:.2f}" if loss is not None else "",
                f"{jitter:.2f}" if jitter is not None else ""
            ])
            self.csv_file.flush()

        parts = [f"[{int(elapsed):03d}s] [Client:{ip}:{port}]"]

        if bandwidth is not None:
            parts.append(f"Bandwidth: {bandwidth:.2f} Mbps")
        if loss is not None:
            parts.append(f"Loss: {loss:.2f}%")
        if jitter is not None:
            parts.append(f"Jitter: {jitter:.6f} ms")

        print(" ".join(parts))

    def summary(self) -> None:
        """
        Print summary statistics
        1. Duration of the test
        2. Number of measurements
        3. For each metric (bandwidth, loss, jitter):
           - Average
           - Minimum
           - Maximum
        4. If CSV output was enabled, print the path to the CSV file
        """
        if not self.stats:
            print(f"{Logger.INFO}No statistics recorded")
            return

        print(f"\n{Logger.INFO}=== Test Summary ===")
        print(
            f"  Duration: {int(self.stats[-1].timestamp - self.stats[0].timestamp)}s")
        print(f"  Measurements: {len(self.stats)}")

        # Calculate averages
        bw_values = [
            s.bandwidth for s in self.stats if s.bandwidth is not None]
        loss_values = [s.loss for s in self.stats if s.loss is not None]
        jitter_values = [s.jitter for s in self.stats if s.jitter is not None]

        if bw_values:
            print(f"  Bandwidth: avg={sum(bw_values)/len(bw_values):.2f} Mbps, "
                  f"min={min(bw_values):.2f}, max={max(bw_values):.2f}")
        if loss_values:
            print(f"  Loss: avg={sum(loss_values)/len(loss_values):.2f}%, "
                  f"min={min(loss_values):.2f}, max={max(loss_values):.2f}")
        if jitter_values:
            print(f"  Jitter: avg={sum(jitter_values)/len(jitter_values):.6f} ms, "
                  f"min={min(jitter_values):.6f}, max={max(jitter_values):.6f}")

        if self.csv_output:
            self.log_success(f"Results saved to {self.csv_output}")

    def close(self) -> None:
        """Close CSV file if open"""
        if self.csv_file:
            self.csv_file.close()

    def log_info(self, message: str) -> None:
        """
        Print an info message to stdout
        """
        print(f"{Logger.INFO}{message}")

    def log_error(self, message: str) -> None:
        """
        Print an info message to stdout
        """
        print(f"{Logger.ERROR}{message}")

# Below you can find sample function signatures for the net-tester client and server.
# You can modify them as needed.


# ---------------------- TCP stubs (Task 2) ----------------------

def tester_tcp_client(log: Logger, server_ip: str, server_port: int,
                      duration: int, interval: int) -> None:
    """TCP client (Task 2)
    TODO:
      - Connect and send for 'duration' seconds (chunks of 'window')
      - Every 'interval' seconds, compute and log bandwidth
    """
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    log.log_info(f"Starting TCP client to {server_ip}:{server_port} "
                 f"for {duration}s")

    # Connect to server
    server_socket.connect((server_ip, server_port))

    # Create a message with size 64 KB
    encoded_message = ("x" * 65536).encode()

    # Time at which the bandwidth test starts
    start_time = time.time()

    # Continously send data until the time elapsed is greater than or equal to the specified duration of the test
    while time.time() - start_time < duration:

        # Variable to store the time at the beginning of the interval
        interval_start = time.time()

        # Variable to record the amount of data it has sent to the server
        size_of_data = 0

        while time.time() - interval_start < interval:

            server_socket.sendall(encoded_message)
            size_of_data += len(encoded_message)

        # Bandwidth (Mbps) = (data (bytes) * 8 (bits)) / 1024) (Mbits) / time (seconds)
        bandwidth = ((size_of_data * 8) / 1000000) / interval

        # Log the bandwidth
        log.log_stat(time.time(), server_ip, server_port, bandwidth)

    # Close the TCP socket
    server_socket.close()
    # Skeleton only; safe no-op if not implemented.
    return None


def tester_tcp_server(log: Logger, port: int) -> None:
    """TCP server (Task 2)
    TODO:
      - Listen on 'port'; accept multiple clients
      - Receive/discard bytes; optionally log per-client bandwidth
    """
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    log.log_info(f"Starting TCP server on port {port}")

    server_socket.bind(("", port))

    server_socket.listen()

    while True:

        # Accept incoming connections
        connection_socket, addr = server_socket.accept()

        if not connection_socket:
            break

        # Create a thread for every incoming client
        threading.Thread(target=handle_tcp_client, args=(
            connection_socket, addr)).start()

    server_socket.close()

    # Skeleton only; safe no-op if not implemented.
    return None


def handle_tcp_client(connection_socket, addr):

    while True:

        received_message = connection_socket.recv(65536)

        # If there is no incoming packet from the socket, break from loop and close the socket
        if not received_message:
            break

    print(f"Connection socket with address: {addr} closed")
    connection_socket.close()

    # ---------------------- UDP stubs (Tasks 3 & 4) ----------------------


def tester_udp_client(log: Logger, server_ip: str, server_port: int,
                      duration: int, interval: int,
                      rate_kbps: int, ack: bool) -> None:
    """UDP client
    Task 3 (ack == False):
      - Send datagrams at 'rate_kbps'
      - First 4 bytes = big-endian ID; start at 1; send ID=0 to end
      - Client may log sending rate, but server computes metrics
    Task 4 (ack == True):
      - Receive acks (ID + server receive timestamp)
      - Compute client-side BW / loss (via timeout) / jitter from acks and log
    """
    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    log.log_info(f"Starting UDP client to {server_ip}:{server_port} "
                 f"for {duration}s at {rate_kbps} Kbps (ack={ack})")
    # Common setup (safe if left unused):
    # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Do not forget to bind the client socket to a port if you want to receive ACKs

    if not ack:
        # -------------------- Task 3: UDP without acks --------------------
        # TODO:
        #   - Compute packet trasmission interval to match rate_kbps using you datagram size
        #   - Loop until 'duration' elapsed:
        #       * Build payload: 4B ID (big-endian) + (pkt_size-4) bytes
        #       * sendto(...)
        #       * sleep until next send (pkt_interval)
        #       * every 'interval' seconds, optionally log sending rate
        #   - Send ID=0 to signal end; close socket

        # Variable to store IDs of each packet
        ID = 1

        # Calculate the transmission interval (time between each send)
        rate_bps = (rate_kbps * 1024) / 8
        payloads_persec = rate_bps / 1472
        time_between_sends = 1 / payloads_persec

        start_time = time.time()
        interval_start = time.time()

        while time.time() - start_time < duration:

            # Create a payload with ID (increments for each payload)
            payload = ID.to_bytes(4, "big")
            payload += (b"x" * 1468)

            client_socket.sendto(payload, (server_ip, server_port))

            time_to_sleep = time_between_sends - (time.time() - interval_start)

            # Sleep for __ time to stay on the rate
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)

            # Reset interval start to current time
            interval_start = time.time()

            # Increment ID of payload
            ID += 1

        # Send payload with ID 0 to end (after the duration of the test has passed)
        ID = 0
        payload = ID.to_bytes(4, "big") + (b"x" * 1468)
        client_socket.sendto(payload, (server_ip, server_port))

        # Close the socket
        client_socket.close()

        return None
    else:
        # -------------------- Task 4: UDP with acks --------------------
        # TODO:
        #   - Same sending loop as Task 3
        #   - Keep track of pending ACKs and received ACK timestamps
        #   - Non-blocking recv for acks:
        #       * parse 4B ID + server-timestamp (specify your chosen encoding)
        #       * compute RTT / arrival deltas; update metrics
        #   - Every 'interval' seconds, log client-side BW/loss/jitter via log.report(...)
        #   - End with ID=0; close socket
        return None


def tester_udp_server(log: Logger, port: int, rate: int, interval: int, ack: bool) -> None:
    """UDP server
    Task 3 (ack == False):
      - Receive datagrams from multiple clients (track by (ip,port))
      - Compute per-client bandwidth / jitter / loss from arrivals
      - Periodically log per-client metrics via log.report(...)
    Task 4 (ack == True):
      - Same as Task 3, plus send an ack for each received datagram:
        4B ID (big-endian)
    """

    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    log.log_info(f"Starting UDP server on port {port} (ack={ack})")

    server_socket.bind(("", port))

    # List for per-client statistics
    list_of_clients_statistics = {}

    # Common setup (safe if left unused):
    # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock.bind(("0.0.0.0", port))

    if not ack:
        # -------------------- Task 3: server-only metrics --------------------
        # TODO:
        #   - recvfrom(...) loop
        #   - Parse ID from first 4B; update per-client stats
        #   - When elapsed >= interval (per client), compute:
        #       * bandwidth (bytes/elapsed)
        #       * loss = 1 - (recv_count / (max_id - min_id + 1))
        #       * jitter from consecutive arrival deltas
        #     then log via: log.report("server", ip, port, bandwidth=..., loss=..., jitter=...)

        # Variable to tell when the test finishes (payload with ID=0 is received)
        endTest = False

        while True:

            if endTest:
                break

            # Variable to store interval start time
            interval_start = time.time()

            # Go on a loop until an interval has passed
            while time.time() - interval_start < interval:

                # Receive incoming messages with their address (client)
                message, addr = server_socket.recvfrom(1472)

                # If there is no incoming packet from the socket, break from loop and close the socket
                if not message:
                    break

                # Extract the header ID of the payload
                header_id = int.from_bytes(message[:4], "big")

                if header_id == 0:

                    # Remove client from dictionary
                    del list_of_clients_statistics[addr]
                    log.log_info(
                        f"Received termination datagram (ID 0); finishing UDP session for client {addr[0]}:{addr[1]}")

                    # If dictionary has no clients anymore, close server socket
                    if len(list_of_clients_statistics) == 0:
                        endTest = True
                    break

                # Add the statistics to the client using a dictionary
                if not addr in list_of_clients_statistics:

                    # If it is a new client create a new entry in the dictionary
                    new_client = {addr: {
                        "list_of_datagrams": [header_id], "num_of_received": 1, "num_of_sent": 0,
                        "arrival_times": [time.time()], "size_of_data": len(message)
                    }}
                    list_of_clients_statistics.update(new_client)
                else:

                    # If the client already exists in the dictinary, update values
                    # Increment num_of_received packets by 1
                    list_of_clients_statistics[addr]["num_of_received"] += 1

                    # Add the packet's ID to the list_of_datagrams list
                    list_of_clients_statistics[addr]["list_of_datagrams"].append(
                        header_id)

                    # Add the packet's arrival time to the arrival_times list
                    list_of_clients_statistics[addr]["arrival_times"].append(
                        time.time())

                    # Add the size of the data packet received to the total data size
                    list_of_clients_statistics[addr]["size_of_data"] += len(
                        message)

            # --- After each interval, calculate bandwidth, packet loss, and jitter and log --- #

            for addr, stats in list_of_clients_statistics.items():

                # Calculate the number of sent packets using IDs
                num_of_sent = max(stats["list_of_datagrams"]) - min(
                    stats["list_of_datagrams"]) + 1
                stats["num_of_sent"] = num_of_sent

                # Bandwidth (Mbps) = (data (bytes) * 8 (bits)) / 1000000) (Mbits) / time (seconds)
                bandwidth = ((stats["size_of_data"] * 8) / 1000000) / interval

                # Packet loss (%) = (1 - (Received datagrams / Sent datagrams)) * 100
                packet_loss = (1 - (stats["num_of_received"] /
                                    stats["num_of_sent"])) * 100

                # Calculate the transmission interval
                rate_bps = (rate * 1024) / 8
                payloads_persec = rate_bps / 1472
                I = 1 / payloads_persec

                # N = # of received packets
                # I = transmission interval
                # T(i) = arrival time of packet i

                # Create variables for number of received, list of datagrams received and their received timestamps
                num_of_received = stats["num_of_received"]
                datagrams = stats["list_of_datagrams"]
                arrival_times = stats["arrival_times"]

                # If the num of received packets is less than 2 then jitter is 0
                if num_of_received < 2:
                    jitter = 0
                else:
                    count = 0
                    total_jitter = 0

                    # Loop to go through the datagrams received count them and calculate total jitter
                    for i in range(0, num_of_received - 1):
                        if datagrams[i] + 1 == datagrams[i+1]:
                            total_jitter += abs(
                                (arrival_times[i+1] - arrival_times[i]) - I)
                            count += 1

                    # Calculate jitter by dividing total jitter by number of datagrams received (* 1000 to get it in ms)
                    jitter = (total_jitter / count) * 1000

                # Log the bandwidth(Mbps), jitter(ms), and packet loss
                log.log_stat(time.time(), addr, port,
                             bandwidth, packet_loss, jitter)

                # Reset client statistics
                list_of_clients_statistics[addr] = {
                    "list_of_datagrams": [], "num_of_received": 0,
                    "num_of_sent": 0, "arrival_times": [], "size_of_data": 0
                }

        # Close the server socket
        server_socket.close()

        return None
    else:
        # -------------------- Task 4: add acknowledgements --------------------
        # TODO:
        #   - Same as above, and for each received datagram:
        #       * Build ack: 4B ID + timestamp (e.g., float via struct.pack)
        #       * sendto(ack, (ip, port))
        #   - Continue periodic logging as in Task 3
        # Variable to tell when the test finishes (payload with ID=0 is received)
        endTest = False

        while True:

            if endTest:
                break

            # Variable to store interval start time
            interval_start = time.time()

            # Go on a loop until an interval has passed
            while time.time() - interval_start < interval:

                # Receive incoming messages with their address (client)
                message, addr = server_socket.recvfrom(1472)

                # Send ACK
                server_socket.sendto(message[:4], addr)

                # If there is no incoming packet from the socket, break from loop and close the socket
                if not message:
                    break

                # Extract the header ID of the payload
                header_id = int.from_bytes(message[:4], "big")

                if header_id == 0:

                    # Remove client from dictionary
                    del list_of_clients_statistics[addr]
                    log.log_info(
                        f"Received termination datagram (ID 0); finishing UDP session for client {addr[0]}:{addr[1]}")

                    # If dictionary has no clients anymore, close server socket
                    if len(list_of_clients_statistics) == 0:
                        endTest = True
                    break

                # Add the statistics to the client using a dictionary
                if not addr in list_of_clients_statistics:

                    # If it is a new client create a new entry in the dictionary
                    new_client = {addr: {
                        "list_of_datagrams": [header_id], "num_of_received": 1, "num_of_sent": 0,
                        "arrival_times": [time.time()], "size_of_data": len(message)
                    }}
                    list_of_clients_statistics.update(new_client)
                else:

                    # If the client already exists in the dictinary, update values
                    # Increment num_of_received packets by 1
                    list_of_clients_statistics[addr]["num_of_received"] += 1

                    # Add the packet's ID to the list_of_datagrams list
                    list_of_clients_statistics[addr]["list_of_datagrams"].append(
                        header_id)

                    # Add the packet's arrival time to the arrival_times list
                    list_of_clients_statistics[addr]["arrival_times"].append(
                        time.time())

                    # Add the size of the data packet received to the total data size
                    list_of_clients_statistics[addr]["size_of_data"] += len(
                        message)

            # --- After each interval, calculate bandwidth, packet loss, and jitter and log --- #

            for addr, stats in list_of_clients_statistics.items():

                # Calculate the number of sent packets using IDs
                num_of_sent = max(stats["list_of_datagrams"]) - min(
                    stats["list_of_datagrams"]) + 1
                stats["num_of_sent"] = num_of_sent

                # Bandwidth (Mbps) = (data (bytes) * 8 (bits)) / 1000000) (Mbits) / time (seconds)
                bandwidth = ((stats["size_of_data"] * 8) / 1000000) / interval

                # Packet loss (%) = (1 - (Received datagrams / Sent datagrams)) * 100
                packet_loss = (1 - (stats["num_of_received"] /
                                    stats["num_of_sent"])) * 100

                # Calculate the transmission interval
                rate_bps = (rate * 1024) / 8
                payloads_persec = rate_bps / 1472
                I = 1 / payloads_persec

                # N = # of received packets
                # I = transmission interval
                # T(i) = arrival time of packet i

                # Create variables for number of received, list of datagrams received and their received timestamps
                num_of_received = stats["num_of_received"]
                datagrams = stats["list_of_datagrams"]
                arrival_times = stats["arrival_times"]

                # If the num of received packets is less than 2 then jitter is 0
                if num_of_received < 2:
                    jitter = 0
                else:
                    count = 0
                    total_jitter = 0

                    # Loop to go through the datagrams received count them and calculate total jitter
                    for i in range(0, num_of_received - 1):
                        if datagrams[i] + 1 == datagrams[i+1]:
                            total_jitter += abs(
                                (arrival_times[i+1] - arrival_times[i]) - I)
                            count += 1

                    # Calculate jitter by dividing total jitter by number of datagrams received (* 1000 to get it in ms)
                    jitter = (total_jitter / count) * 1000

                # Log the bandwidth(Mbps), jitter(ms), and packet loss
                log.log_stat(time.time(), addr, port,
                             bandwidth, packet_loss, jitter)

                # Reset client statistics
                list_of_clients_statistics[addr] = {
                    "list_of_datagrams": [], "num_of_received": 0,
                    "num_of_sent": 0, "arrival_times": [], "size_of_data": 0
                }

        # Close the server socket
        server_socket.close()

        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="SCC.231 net-tester application")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("-s", "--server", action="store_true",
                      help="Run in server mode")
    mode.add_argument("-c", "--client", metavar="ADDR",
                      help="Run in client mode, connect to ADDR")

    parser.add_argument("-p", "--port", type=int,
                        default=5001, help="Port (default 5001)")
    parser.add_argument("-u", "--udp", action="store_true",
                        help="Use UDP (default TCP)")
    parser.add_argument("-a", "--ack", action="store_true",
                        help="(UDP) Enable acknowledgements")
    parser.add_argument("-t", "--duration", type=int,
                        default=60, help="Test duration seconds (default 60)")
    parser.add_argument("-i", "--interval", type=int, default=1,
                        help="Report interval seconds (default 1)")
    parser.add_argument("-r", "--rate", type=int, default=1000,
                        help="(UDP) send rate Kbps (default 1000)")
    parser.add_argument('-l', '--log', type=str, default=None,
                        help='Path to CSV log file (default: None)')

    args = parser.parse_args()
    log = Logger(csv_output=args.log)

    if args.server:
        if args.udp:
            # Task 3/4 (no-op until implemented)
            tester_udp_server(log, args.port, args.rate,
                              args.interval, args.ack)
        else:
            # Task 2 (no-op until implemented)
            tester_tcp_server(log, args.port)
    else:
        if args.udp:
            tester_udp_client(log, args.client, args.port,
                              args.duration, args.interval,
                              args.rate, args.ack)        # Task 3/4 (no-op until implemented)
        else:
            tester_tcp_client(log, args.client, args.port,
                              args.duration, args.interval)  # Task 2 (no-op until implemented)
    log.summary()
    log.close()
