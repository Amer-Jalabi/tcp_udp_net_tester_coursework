# Network Bandwidth Measurement Tool

A Python-based client–server application developed as part of university coursework to measure network bandwidth and related performance metrics using both **TCP** and **UDP**.

## Overview

This project implements configurable TCP and UDP bandwidth tests between a client and a server.  
It measures throughput over a fixed duration and reports real-time network metrics, allowing comparison between transport protocols under different conditions.

The system is designed to be lightweight, modular, and easy to extend for experimentation with networking concepts.

## Features

- TCP and UDP client–server implementations using Python sockets
- Configurable test duration, packet size, and reporting interval
- Real-time bandwidth calculation
- Measurement of:
  - Throughput (bandwidth)
  - Packet loss (UDP)
  - Jitter (UDP)
- Multi-threaded TCP server supporting multiple concurrent clients
- Detailed logging for post-test analysis

## Technologies Used

- **Language:** Python
- **Networking:** TCP & UDP sockets
- **Concurrency:** Python threading
- **Environment:** Linux / University VM

## How It Works

1. The server listens for incoming TCP or UDP connections.
2. The client sends data packets continuously for a specified duration.
3. The server records received data and timestamps.
4. Bandwidth and other metrics are calculated and logged during and after the test.

## Usage (Example)

Before running the server run (in an empty terminal):
```bash
xhost +

Start the server:
```bash
make

Run as many clients and a single server using:
```bash
xterm <hostname1> <hostname2> <hostname3> ...

In each host type:
```bash
python3 net-tester.py 

Then continue with either -s for server or -c <server_ip> for client.

For client:
Add -p <port>
Add -t <time_in_seconds> for time of test
Add -i <time_in_seconds> for time of each interval (logs)

Add -u for UDP for both server and client
