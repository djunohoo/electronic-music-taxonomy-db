# MetaCrate Multi-User System v1.8

**Complete per-user control and management system for MetaCrate music scanning operations.**

## 🎯 Overview

This enhanced system allows **multiple MetaCrate users to run independently** with:

- **Per-user scan control** (start/stop individual users)
- **Concurrent user processing** (multiple users can scan simultaneously)
- **User-specific progress tracking** and statistics
- **Real-time web dashboard** with live monitoring
- **CLI controller** for command-line management
- **User-specific Twitch notifications**
- **Flexible configuration** per user

## 📁 System Components

### 1. `metacrate_multiuser_orchestrator_v1.8.py`
**Core multi-user orchestration engine**

**Features:**
- Auto-discovers users from `X:\lightbulb networ IUL Dropbox\Automation\MetaCrate\USERS\`
- Concurrent user processing with ThreadPoolExecutor
- Per-user configuration (batch size, intervals, priority)
- Individual user statistics and progress tracking
- User-specific Twitch notifications
- Thread-safe user management

**Key Classes:**
- `MetaCrateMultiUserOrchestrator` - Main orchestration class
- `UserScanConfig` - Per-user configuration settings
- `UserStats` - Individual user statistics and progress
- `TwitchBot` - User-specific Twitch notifications

### 2. `metacrate_user_controller.py` 
**Command-line interface for user management**

**Features:**
- Interactive CLI mode with commands
- Start/stop individual users
- Enable/disable users
- Bulk operations (start all, stop all)
- Real-time status monitoring
- User configuration management

**Usage Examples:**
```bash
# Interactive mode
python metacrate_user_controller.py

# Direct commands
python metacrate_user_controller.py --start DJUNOHOO
python metacrate_user_controller.py --stop DJUNOHOO
python metacrate_user_controller.py --status
python metacrate_user_controller.py --start-all
```

### 3. `metacrate_multiuser_dashboard.py`
**Real-time web dashboard with monitoring and control**

**Features:**
- Live status monitoring with WebSocket updates
- Per-user control buttons (start/stop/enable/disable)
- Real-time progress bars and statistics
- Global controls (start all, stop all)
- Responsive web design
- RESTful API endpoints

**Access:** http://localhost:8082

### 4. `setup_metacrate_multiuser.py`
**Setup and launcher script**

**Features:**
- Dependency installation
- System validation
- Configuration file creation
- Component testing
- Easy launcher for dashboard or CLI

## 🚀 Quick Start

### 1. Setup System
```bash
# Install dependencies
python setup_metacrate_multiuser.py install

# Check MetaCrate directory
python setup_metacrate_multiuser.py check

# Create example configuration
python setup_metacrate_multiuser.py config

# Test the system
python setup_metacrate_multiuser.py test
```

### 2. Launch Dashboard (Recommended)
```bash
python setup_metacrate_multiuser.py dashboard
```
Then open: http://localhost:8082

### 3. Launch CLI Controller
```bash
python setup_metacrate_multiuser.py cli
```

## 🎮 Usage Guide

### Web Dashboard Operations

1. **Monitor Users:** Real-time status updates every 5 seconds
2. **Individual Control:** Start/Stop/Enable/Disable per user
3. **Bulk Operations:** Start all enabled users or stop all users
4. **Progress Tracking:** Visual progress bars and file counts
5. **Configuration:** View user settings and statistics

### CLI Controller Commands

```
metacrate> help                    # Show all commands
metacrate> list                     # List all users
metacrate> status                   # Show detailed status
metacrate> start DJUNOHOO          # Start specific user
metacrate> stop DJUNOHOO           # Stop specific user
metacrate> enable DJUNOHOO         # Enable user
metacrate> disable DJUNOHOO        # Disable user
metacrate> start-all               # Start all enabled users
metacrate> stop-all                # Stop all users
metacrate> config DJUNOHOO         # Show user configuration
metacrate> quit                     # Exit controller
```

### Python API Usage

```python
from metacrate_multiuser_orchestrator_v1_8 import MetaCrateMultiUserOrchestrator

# Create orchestrator
orchestrator = MetaCrateMultiUserOrchestrator(max_concurrent_users=3)

# Configure specific user
orchestrator.configure_user("DJUNOHOO", batch_size=100, interval_minutes=10)

# Control individual users
orchestrator.start_user_scan("DJUNOHOO")
orchestrator.stop_user_scan("DJUNOHOO")

# Bulk operations
orchestrator.start_all_users()
orchestrator.stop_all_users()

# Get statistics
user_stats = orchestrator.get_user_stats("DJUNOHOO")
all_stats = orchestrator.get_user_stats()
```

## ⚙️ Configuration

### User Configuration Options

```python
UserScanConfig(
    username="DJUNOHOO",
    batch_size=250,           # Files per batch
    interval_minutes=15,      # Minutes between scans
    enabled=True,            # Enable/disable user
    priority=5,              # Priority 1-10 (higher = more priority)
    twitch_notifications=False  # Enable Twitch updates
)
```

### System Configuration

```python
MetaCrateMultiUserOrchestrator(
    max_concurrent_users=3   # Maximum users running simultaneously
)
```

### Twitch Integration

```python
# Setup Twitch notifications
orchestrator.setup_twitch_bot(
    username="your_bot_username",
    oauth_token="oauth:your_token",
    channel="your_channel"
)
```

## 📊 Monitoring and Statistics

### Per-User Statistics
- **Total Files:** Files discovered in user directory
- **Processed Files:** Files successfully processed
- **Skipped Files:** Files already processed (deduplication)
- **Error Files:** Files that failed processing
- **Batches Completed:** Number of batch operations completed
- **Last Scan:** Timestamp of last scan operation
- **Scan Duration:** Time taken for last scan
- **Running Status:** Current operation status

### Global Statistics
- **Total Users:** All discovered users
- **Running Users:** Currently active scans
- **Enabled Users:** Users configured for scanning
- **Max Concurrent:** System concurrency limit

## 🔧 Technical Details

### Directory Structure
```
MetaCrate USERS Directory:
X:\lightbulb networ IUL Dropbox\Automation\MetaCrate\USERS\
├── DJUNOHOO\           # User-specific music collection
├── USER2\              # Another user's collection
└── USER3\              # Third user's collection
```

### Processing Flow
1. **Discovery:** Auto-discover users from USERS directory
2. **Configuration:** Load per-user settings and preferences
3. **Batch Processing:** Process files in configurable batch sizes
4. **Deduplication:** Skip already processed files using hashes
5. **Statistics:** Track progress and performance metrics
6. **Notifications:** Send updates via Twitch (optional)

### Concurrency Control
- **Thread Pool:** Manages concurrent user processing
- **Stop Events:** Graceful shutdown per user
- **Resource Limits:** Configurable maximum concurrent users
- **Priority System:** User-based processing priority

### API Endpoints

**Web Dashboard API:**
- `GET /api/users` - Get all users and statistics
- `POST /api/control` - Control user operations
- `POST /api/configure` - Update user configuration
- `POST /api/start-all` - Start all enabled users
- `POST /api/stop-all` - Stop all users
- `WebSocket /ws` - Real-time updates

## 🛠️ Troubleshooting

### Common Issues

**1. MetaCrate Directory Not Found**
```
Error: MetaCrate USERS directory not found
Solution: Ensure X:\lightbulb networ IUL Dropbox\Automation\MetaCrate\USERS exists
```

**2. No Users Discovered**
```
Error: No users found in directory
Solution: Check that user directories exist under USERS folder
```

**3. User Won't Start**
```
Error: Failed to start user
Solutions:
- Check if user is enabled
- Verify maximum concurrent users not exceeded
- Ensure user directory is accessible
```

**4. Dashboard Won't Load**
```
Error: Dashboard not accessible
Solutions:
- Check port 8082 is available
- Install required dependencies: fastapi, uvicorn
- Run setup_metacrate_multiuser.py install
```

### Logging

All components log to individual files:
- `metacrate_multiuser_orchestrator.log` - Core system logs
- Console output for real-time monitoring

### Performance Tuning

**Optimize for Speed:**
- Increase `batch_size` (e.g., 500)
- Decrease `interval_minutes` (e.g., 5)
- Increase `max_concurrent_users` (e.g., 5)

**Optimize for Stability:**
- Decrease `batch_size` (e.g., 100)
- Increase `interval_minutes` (e.g., 30)
- Decrease `max_concurrent_users` (e.g., 2)

## 🔄 Migration from Single-User

If upgrading from the original batch orchestrator:

1. **Backup Existing Data:** Export current database
2. **Install New System:** Run setup script
3. **Configure Users:** Set per-user preferences
4. **Test Individual Users:** Start with one user
5. **Scale Up:** Gradually enable more users

## 🎵 Real-World Usage Scenarios

### Scenario 1: DJ with Multiple Music Collections
- **DJUNOHOO:** Personal collection (high priority, small batches)
- **DJUNOHOO_WORK:** Professional tracks (standard processing)
- **DJUNOHOO_ARCHIVE:** Old collection (low priority, large batches)

### Scenario 2: Music Label with Multiple Artists
- **ARTIST1:** Active releases (frequent scanning)
- **ARTIST2:** Catalog tracks (weekly scanning)
- **LABEL_ARCHIVE:** Historical releases (monthly scanning)

### Scenario 3: Collaborative Music Platform
- **USER_A:** Electronic music specialist
- **USER_B:** Hip-hop collection
- **USER_C:** Classical and ambient
- **SHARED:** Community uploads

## 📈 Future Enhancements

**Planned Features:**
- User-specific genre preferences
- Scheduled scanning (cron-like functionality)
- Email notifications in addition to Twitch
- Advanced filtering and search
- Export capabilities per user
- Integration with music streaming platforms
- Machine learning recommendations per user

**Performance Improvements:**
- Parallel file processing within batches
- Smart scheduling based on system resources
- Adaptive batch sizing based on performance
- Predictive processing based on user patterns

---

**System Version:** MetaCrate Multi-User v1.8  
**Last Updated:** January 2025  
**Author:** AI Assistant  
**License:** MIT  

For support or feature requests, please refer to the project documentation or contact the development team.