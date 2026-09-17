# Network Bandwidth Measurement Tool

A Python-based client–server application developed as part of university coursework to measure network bandwidth and related performance metrics using both **TCP** and **UDP**.

**Coursework note:** This project was developed as part of university coursework using a university-provided starter codebase. The repository contains both provided framework code and my own implementation.

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

The tool measures network bandwidth using both TCP and UDP protocols:

- **TCP**: The client connects to the server, sends data, and calculates real-time bandwidth, packet loss, and jitter. All TCP metrics are **logged and saved on the client side**.  
- **UDP**: The client sends packets to the server without acknowledgments. Metrics such as packet loss and bandwidth are **calculated and logged on the server side**.  

Multi-threading is used to handle multiple clients concurrently:  
- For TCP, one thread per client on the server manages the connection.  
- For UDP, the server processes incoming packets from multiple clients simultaneously.

## Usage

Before running the server run (in an empty terminal):
```bash
xhost +
```

Start the server:
```bash
make
```

Run as many clients and a single server using:
```bash
xterm <hostname1> <hostname2> <hostname3> ...
```

In each host type:
```bash
python3 net-tester.py
```

Then continue with either -s for server or -c <server_ip> for client.

For client: <br>
Add -p <port> <br>
Add -t <time_in_seconds> for time of test <br>
Add -i <time_in_seconds> for time of each interval (logs) <br>

Add -u for UDP for both server and client

Make sure to run the server before running the client/s.
