# Quick Start Guide - Project Sentinel

## 🚀 Get Started in 3 Steps

### Step 1: Navigate to Executables
```bash
cd evidence/executables
```

### Step 2: Run the Demo
```bash
python run_demo.py
```

### Step 3: View Results
- Events are saved to `evidence/output/test/events.jsonl` and `evidence/output/final/events.jsonl`
- Open dashboard at `http://localhost:5000` (if prompted)

---

## 📊 What Gets Generated

1. **events.jsonl** - All detected events in required format
2. **summary.json** - Statistical summary of detections
3. **statistics.json** - Detailed analytics
4. **Dashboard** - Real-time visualization (optional)

---

## 🎯 Event Types Detected

### Fraud & Theft (High Priority)
- ✅ **Scanner Avoidance** - Items detected by RFID but not scanned at POS
- ✅ **Barcode Switching** - Visual system detects different product than scanned
- ✅ **Weight Discrepancies** - Actual weight differs significantly from expected

### Operational Issues
- ✅ **Long Queue Length** - Too many customers waiting (>5)
- ✅ **Long Wait Time** - Excessive dwell time (>300 seconds)
- ✅ **System Crashes** - Gaps in event stream indicating downtime
- ✅ **Staffing Needs** - Recommendations for additional staff

### Inventory Management
- ✅ **Inventory Discrepancies** - Mismatch between expected and actual inventory
- ✅ **Successful Operations** - Baseline tracking of normal transactions

---

## 🔧 Advanced Usage

### Custom Data Directory
```bash
python run_demo.py /path/to/custom/data/input
```

### Run Without Dashboard
Edit `run_demo.py` and respond 'n' when prompted

### Run Individual Components

**Process Data Only:**
```bash
cd src
python main.py --data-dir /path/to/data --output output/events.jsonl --summary
```

**Start Dashboard Only:**
```bash
cd src
python dashboard.py --events-file ../evidence/output/test/events.jsonl --port 5000
```

**Visualize Results:**
```bash
cd src
python visualize.py ../evidence/output/test/events.jsonl
```

**Run Tests:**
```bash
cd src
python test_algorithms.py
```

---

## 📈 Understanding the Output

### Event Format
```json
{
  "timestamp": "2025-08-13T16:00:04",
  "event_id": "E001",
  "event_data": {
    "event_name": "Scanner Avoidance",
    "station_id": "SCC1",
    "product_sku": "PRD_T_03"
  }
}
```

### Event IDs
- **E000** - Successful Operation
- **E001** - Scanner Avoidance
- **E002** - Barcode Switching
- **E003** - Weight Discrepancies
- **E004** - System Crash
- **E005** - Long Queue Length
- **E006** - Long Wait Time
- **E007** - Inventory Discrepancy
- **E008** - Staffing Needs
- **E009** - Checkout Station Action

---

## 🎓 For Judges

### Automated Judging
All algorithms are tagged with `# @algorithm Name | Purpose` in `src/algorithms.py`

Verify with:
```bash
grep -r "@algorithm" src/
```

### Directory Structure Compliance
```
Team01_sentinel/
├── README.md ✓
├── SUBMISSION_GUIDE.md ✓
├── src/ ✓ (all source code)
├── evidence/
│   ├── executables/run_demo.py ✓
│   ├── output/
│   │   ├── test/events.jsonl ✓
│   │   └── final/events.jsonl ✓
│   └── screenshots/ (to be captured)
```

### Running the Demo
```bash
cd evidence/executables
python3 run_demo.py
```

This will:
1. Install dependencies automatically
2. Process all data
3. Generate all required outputs
4. Offer to start dashboard

---

## ❓ Troubleshooting

**Q: "Data directory not found"**  
A: Provide explicit path: `python run_demo.py /path/to/data/input`

**Q: "Port 5000 already in use"**  
A: Change port: `python dashboard.py --events-file events.jsonl --port 8080`

**Q: "Module not found"**  
A: Install dependencies: `pip install -r requirements.txt`

**Q: "No events detected"**  
A: Check data directory has all required files (POS, RFID, recognition, queue, inventory)

---

## 💡 Tips for Best Results

1. **Complete Data**: Ensure all data sources are present for comprehensive detection
2. **Threshold Tuning**: Adjust `THRESHOLDS` in `src/config.py` for sensitivity
3. **Dashboard**: Use dashboard for interactive exploration of results
4. **Evidence**: Screenshots capture key insights for presentation

---

## 📞 Support

For questions or issues:
- Review README.md for comprehensive documentation
- Check IMPLEMENTATION_PLAN.md for technical details
- Examine inline code comments for algorithm specifics
- Contact: team01.sentinel@innovatex.com

---

**Ready to detect retail intelligence events? Run `python run_demo.py` now!** 🚀
