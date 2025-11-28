# AgentX - Self-Checkout Fraud Detection System

## Overview

AgentX is an intelligent retail analytics platform designed to detect anomalies and potential fraud in self-checkout systems. The system processes multiple data streams including POS transactions, queue monitoring, RFID readings, product recognition, and inventory snapshots to identify suspicious patterns and generate actionable insights.

### Key Features

- **Multi-Source Data Processing**: Ingests data from POS systems, RFID scanners, cameras, and queue monitors
- **Real-Time Event Detection**: Identifies fraudulent activities and anomalies in real-time
- **Streaming Architecture**: Supports live data streaming for continuous monitoring
- **Interactive Dashboard**: Web-based visualization for monitoring events and statistics
- **Comprehensive Analytics**: Generates detailed summaries and event logs

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/KusalPabasara/codeblast.git
   cd codeblast
   ```

2. **Install dependencies**
   ```bash
   cd AgentX/TeamGmora_AgentX
   pip install -r requirements.txt
   ```

### Running the Application

#### Option 1: Process Data and Generate Events

```bash
cd AgentX/TeamGmora_AgentX/src
python main.py --data-dir ../../../data/input --output ../../../data/output/events.jsonl
```

#### Option 2: Run with Dashboard

```bash
python main.py --data-dir ../../../data/input --output ../../../data/output/events.jsonl --dashboard
```

The dashboard will be available at `http://localhost:5000`

#### Option 3: Start Streaming Server

```bash
cd data/streaming-server
python stream_server.py --port 8765 --speed 1.0
```

## 📁 Project Structure

```
AgentX/
├── data/                          # Data directory
│   ├── input/                     # Input datasets
│   │   ├── customer_data.csv
│   │   ├── inventory_snapshots.jsonl
│   │   ├── pos_transactions.jsonl
│   │   ├── product_recognition.jsonl
│   │   ├── products_list.csv
│   │   ├── queue_monitoring.jsonl
│   │   └── rfid_readings.jsonl
│   ├── output/                    # Generated outputs
│   │   ├── events.jsonl
│   │   └── summary.json
│   ├── streaming-clients/         # Example streaming clients
│   │   ├── client_example.py
│   │   ├── client_example_node.js
│   │   └── ClientExample.java
│   └── streaming-server/          # Real-time streaming server
│       └── stream_server.py
│
├── AgentX/                        # Main application directory
│   └── TeamGmora_AgentX/
│       ├── src/                   # Source code
│       │   ├── algorithms.py      # Detection algorithms
│       │   ├── config.py          # Configuration settings
│       │   ├── dashboard.py       # Web dashboard
│       │   ├── data_loader.py     # Data loading utilities
│       │   ├── event_engine.py    # Event detection engine
│       │   ├── main.py            # Main entry point
│       │   ├── streaming_client.py # Streaming client
│       │   ├── test_algorithms.py # Algorithm tests
│       │   ├── visualize.py       # Visualization utilities
│       │   └── templates/
│       │       └── dashboard.html
│       ├── evidence/              # Test results and screenshots
│       │   ├── executables/
│       │   ├── output/
│       │   └── screenshots/
│       └── requirements.txt       # Python dependencies
│
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## 🔧 Configuration

Edit `AgentX/TeamGmora_AgentX/src/config.py` to customize:

- Detection thresholds
- Data file paths
- Dashboard settings
- Algorithm parameters

## 📊 Data Sources

The system processes the following data types:

| Data Source | Description | Format |
|-------------|-------------|--------|
| POS Transactions | Self-checkout transaction records | JSONL |
| RFID Readings | Product tag readings | JSONL |
| Product Recognition | Camera-based product identification | JSONL |
| Queue Monitoring | Customer queue and movement data | JSONL |
| Inventory Snapshots | Real-time inventory status | JSONL |
| Customer Data | Customer information and history | CSV |
| Products List | Product catalog and pricing | CSV |

## 🛠️ Development

### Running Tests

```bash
cd AgentX/TeamGmora_AgentX/src
python test_algorithms.py
```

### Data Streaming

Start the streaming server to simulate real-time data:

```bash
cd data/streaming-server
python stream_server.py --port 8765 --speed 25 --loop
```

Connect clients using the examples in `data/streaming-clients/`

## 📈 Output Format

### Events (events.jsonl)

Each line contains a detected event:
```json
{
  "event_id": "E001",
  "timestamp": "2024-01-15T10:30:00Z",
  "event_type": "suspicious_activity",
  "severity": "high",
  "description": "Multiple items scanned without RFID confirmation",
  "metadata": {...}
}
```

### Summary (summary.json)

Aggregated statistics and insights:
```json
{
  "total_events": 42,
  "by_severity": {"high": 10, "medium": 20, "low": 12},
  "time_range": {...},
  "top_anomalies": [...]
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Team

**Team Gmora - AgentX**

## 🔗 Links

- [Repository](https://github.com/KusalPabasara/codeblast)
- [Issues](https://github.com/KusalPabasara/codeblast/issues)


