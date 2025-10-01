#!/usr/bin/env python3
"""
MetaCrate Multi-User Web Dashboard v2.0
Real-time monitoring and control dashboard for MetaCrate multi-user operations.

Features:
- Real-time user status monitoring
- Per-user control (start/stop/enable/disable)
- Live statistics and progress tracking
- User configuration management
- Batch processing history
- WebSocket for real-time updates
"""

import json
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import the multi-user orchestrator
from metacrate_multiuser_orchestrator_v1_8 import MetaCrateMultiUserOrchestrator, UserScanConfig, UserStats

class UserControlRequest(BaseModel):
    username: str
    action: str  # start, stop, enable, disable
    
class UserConfigRequest(BaseModel):
    username: str
    batch_size: Optional[int] = None
    interval_minutes: Optional[int] = None
    priority: Optional[int] = None
    twitch_notifications: Optional[bool] = None

class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                # Remove disconnected clients
                self.active_connections.remove(connection)

# Global instances
orchestrator = MetaCrateMultiUserOrchestrator(max_concurrent_users=5)
websocket_manager = WebSocketManager()

# FastAPI app
app = FastAPI(title="MetaCrate Multi-User Dashboard", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def dashboard():
    """Serve the main dashboard HTML"""
    return HTMLResponse(content=get_dashboard_html())

@app.get("/api/users")
async def get_users():
    """Get all users with their current status and statistics"""
    users_data = {}
    
    for username, config in orchestrator.user_configs.items():
        stats = orchestrator.user_stats[username]
        
        users_data[username] = {
            'config': {
                'username': config.username,
                'batch_size': config.batch_size,
                'interval_minutes': config.interval_minutes,
                'enabled': config.enabled,
                'priority': config.priority,
                'twitch_notifications': config.twitch_notifications
            },
            'stats': {
                'total_files': stats.total_files,
                'processed_files': stats.processed_files,
                'skipped_files': stats.skipped_files,
                'error_files': stats.error_files,
                'batches_completed': stats.batches_completed,
                'is_running': stats.is_running,
                'last_scan': stats.last_scan.isoformat() if stats.last_scan else None,
                'session_start': stats.session_start.isoformat() if stats.session_start else None,
                'scan_duration': stats.scan_duration
            }
        }
    
    return {
        'users': users_data,
        'summary': {
            'total_users': len(orchestrator.user_configs),
            'running_users': len(orchestrator.running_users),
            'enabled_users': len([u for u in orchestrator.user_configs.values() if u.enabled]),
            'max_concurrent': orchestrator.max_concurrent_users
        }
    }

@app.post("/api/control")
async def control_user(request: UserControlRequest):
    """Control user scanning (start/stop/enable/disable)"""
    username = request.username.upper()
    action = request.action.lower()
    
    result = {'success': False, 'message': ''}
    
    if action == 'start':
        result['success'] = orchestrator.start_user_scan(username)
        result['message'] = f"Started scanning for {username}" if result['success'] else f"Failed to start {username}"
    
    elif action == 'stop':
        result['success'] = orchestrator.stop_user_scan(username)
        result['message'] = f"Stopped scanning for {username}" if result['success'] else f"Failed to stop {username}"
    
    elif action == 'enable':
        result['success'] = orchestrator.enable_user(username, True)
        result['message'] = f"Enabled {username}" if result['success'] else f"User {username} not found"
    
    elif action == 'disable':
        result['success'] = orchestrator.enable_user(username, False)
        result['message'] = f"Disabled {username}" if result['success'] else f"User {username} not found"
    
    else:
        result['message'] = f"Unknown action: {action}"
    
    # Broadcast update to all connected clients
    if result['success']:
        await websocket_manager.broadcast({
            'type': 'user_update',
            'username': username,
            'action': action,
            'timestamp': datetime.now().isoformat()
        })
    
    return result

@app.post("/api/configure")
async def configure_user(request: UserConfigRequest):
    """Configure user settings"""
    username = request.username.upper()
    
    config_updates = {}
    if request.batch_size is not None:
        config_updates['batch_size'] = request.batch_size
    if request.interval_minutes is not None:
        config_updates['interval_minutes'] = request.interval_minutes
    if request.priority is not None:
        config_updates['priority'] = request.priority
    if request.twitch_notifications is not None:
        config_updates['twitch_notifications'] = request.twitch_notifications
    
    success = orchestrator.configure_user(username, **config_updates)
    
    if success:
        await websocket_manager.broadcast({
            'type': 'config_update',
            'username': username,
            'updates': config_updates,
            'timestamp': datetime.now().isoformat()
        })
    
    return {
        'success': success,
        'message': f"Updated configuration for {username}" if success else f"User {username} not found"
    }

@app.post("/api/start-all")
async def start_all_users():
    """Start scanning for all enabled users"""
    orchestrator.start_all_users()
    
    await websocket_manager.broadcast({
        'type': 'bulk_action',
        'action': 'start_all',
        'timestamp': datetime.now().isoformat()
    })
    
    return {'success': True, 'message': 'Started all enabled users'}

@app.post("/api/stop-all")
async def stop_all_users():
    """Stop scanning for all users"""
    orchestrator.stop_all_users()
    
    await websocket_manager.broadcast({
        'type': 'bulk_action',
        'action': 'stop_all',
        'timestamp': datetime.now().isoformat()
    })
    
    return {'success': True, 'message': 'Stopped all users'}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket_manager.connect(websocket)
    
    try:
        while True:
            # Send periodic status updates
            await asyncio.sleep(5)
            
            users_data = await get_users()
            await websocket.send_text(json.dumps({
                'type': 'status_update',
                'data': users_data,
                'timestamp': datetime.now().isoformat()
            }))
    
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

def get_dashboard_html():
    """Generate the dashboard HTML"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MetaCrate Multi-User Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .header h1 {
            color: white;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .header .subtitle {
            color: rgba(255, 255, 255, 0.8);
            font-size: 1.1em;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .summary-card {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .summary-card h3 {
            font-size: 2em;
            margin-bottom: 5px;
            color: #667eea;
        }
        
        .summary-card p {
            color: #666;
            font-weight: 500;
        }
        
        .controls {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .controls h2 {
            margin-bottom: 15px;
            color: #333;
        }
        
        .control-buttons {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .btn.danger {
            background: #e74c3c;
        }
        
        .btn.danger:hover {
            background: #c0392b;
        }
        
        .users-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }
        
        .user-card {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease;
        }
        
        .user-card:hover {
            transform: translateY(-5px);
        }
        
        .user-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .user-name {
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
        }
        
        .status-badge {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .status-running {
            background: #2ecc71;
            color: white;
        }
        
        .status-stopped {
            background: #e74c3c;
            color: white;
        }
        
        .status-disabled {
            background: #95a5a6;
            color: white;
        }
        
        .user-stats {
            margin-bottom: 15px;
        }
        
        .stat-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        .stat-label {
            color: #666;
        }
        
        .stat-value {
            font-weight: bold;
            color: #333;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #ecf0f1;
            border-radius: 4px;
            margin: 10px 0;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s ease;
        }
        
        .user-controls {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        
        .user-controls .btn {
            flex: 1;
            min-width: 70px;
            padding: 8px 12px;
            font-size: 12px;
        }
        
        .connection-status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: bold;
            z-index: 1000;
        }
        
        .connected {
            background: #2ecc71;
            color: white;
        }
        
        .disconnected {
            background: #e74c3c;
            color: white;
        }
        
        .last-updated {
            text-align: center;
            color: rgba(255, 255, 255, 0.8);
            font-size: 14px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎵 MetaCrate Multi-User Dashboard</h1>
        <div class="subtitle">Real-time monitoring and control for MetaCrate user operations</div>
    </div>
    
    <div class="connection-status" id="connectionStatus">🔌 Connecting...</div>
    
    <div class="container">
        <div class="summary-cards" id="summaryCards">
            <div class="summary-card">
                <h3 id="totalUsers">-</h3>
                <p>Total Users</p>
            </div>
            <div class="summary-card">
                <h3 id="runningUsers">-</h3>
                <p>Running Users</p>
            </div>
            <div class="summary-card">
                <h3 id="enabledUsers">-</h3>
                <p>Enabled Users</p>
            </div>
            <div class="summary-card">
                <h3 id="maxConcurrent">-</h3>
                <p>Max Concurrent</p>
            </div>
        </div>
        
        <div class="controls">
            <h2>🎮 Global Controls</h2>
            <div class="control-buttons">
                <button class="btn" onclick="startAllUsers()">🚀 Start All Users</button>
                <button class="btn danger" onclick="stopAllUsers()">🛑 Stop All Users</button>
                <button class="btn" onclick="refreshData()">🔄 Refresh Data</button>
            </div>
        </div>
        
        <div class="users-grid" id="usersGrid">
            <!-- User cards will be populated here -->
        </div>
        
        <div class="last-updated" id="lastUpdated">
            Last updated: Never
        </div>
    </div>

    <script>
        let ws = null;
        let reconnectInterval = null;
        
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                console.log('WebSocket connected');
                document.getElementById('connectionStatus').textContent = '🟢 Connected';
                document.getElementById('connectionStatus').className = 'connection-status connected';
                
                if (reconnectInterval) {
                    clearInterval(reconnectInterval);
                    reconnectInterval = null;
                }
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                
                if (data.type === 'status_update') {
                    updateDashboard(data.data);
                } else if (data.type === 'user_update') {
                    console.log(`User ${data.username} action: ${data.action}`);
                    refreshData();
                }
            };
            
            ws.onclose = function() {
                console.log('WebSocket disconnected');
                document.getElementById('connectionStatus').textContent = '🔴 Disconnected';
                document.getElementById('connectionStatus').className = 'connection-status disconnected';
                
                // Try to reconnect every 5 seconds
                if (!reconnectInterval) {
                    reconnectInterval = setInterval(connectWebSocket, 5000);
                }
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
        }
        
        function updateDashboard(data) {
            // Update summary cards
            document.getElementById('totalUsers').textContent = data.summary.total_users;
            document.getElementById('runningUsers').textContent = data.summary.running_users;
            document.getElementById('enabledUsers').textContent = data.summary.enabled_users;
            document.getElementById('maxConcurrent').textContent = data.summary.max_concurrent;
            
            // Update users grid
            const usersGrid = document.getElementById('usersGrid');
            usersGrid.innerHTML = '';
            
            Object.entries(data.users).forEach(([username, userData]) => {
                const userCard = createUserCard(username, userData);
                usersGrid.appendChild(userCard);
            });
            
            // Update last updated time
            document.getElementById('lastUpdated').textContent = 
                `Last updated: ${new Date().toLocaleTimeString()}`;
        }
        
        function createUserCard(username, userData) {
            const card = document.createElement('div');
            card.className = 'user-card';
            
            const config = userData.config;
            const stats = userData.stats;
            
            // Determine status
            let statusClass = 'status-stopped';
            let statusText = 'Stopped';
            
            if (!config.enabled) {
                statusClass = 'status-disabled';
                statusText = 'Disabled';
            } else if (stats.is_running) {
                statusClass = 'status-running';
                statusText = 'Running';
            }
            
            // Calculate progress
            const progress = stats.total_files > 0 ? 
                (stats.processed_files / stats.total_files) * 100 : 0;
            
            card.innerHTML = `
                <div class="user-header">
                    <div class="user-name">${username}</div>
                    <div class="status-badge ${statusClass}">${statusText}</div>
                </div>
                
                <div class="user-stats">
                    <div class="stat-row">
                        <span class="stat-label">Files Processed:</span>
                        <span class="stat-value">${stats.processed_files}/${stats.total_files}</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${progress}%"></div>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Batches Completed:</span>
                        <span class="stat-value">${stats.batches_completed}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Error Files:</span>
                        <span class="stat-value">${stats.error_files}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Batch Size:</span>
                        <span class="stat-value">${config.batch_size}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Interval:</span>
                        <span class="stat-value">${config.interval_minutes}m</span>
                    </div>
                </div>
                
                <div class="user-controls">
                    <button class="btn" onclick="controlUser('${username}', 'start')" 
                            ${stats.is_running ? 'disabled' : ''}>Start</button>
                    <button class="btn danger" onclick="controlUser('${username}', 'stop')"
                            ${!stats.is_running ? 'disabled' : ''}>Stop</button>
                    <button class="btn" onclick="controlUser('${username}', '${config.enabled ? 'disable' : 'enable'}')"
                            >${config.enabled ? 'Disable' : 'Enable'}</button>
                </div>
            `;
            
            return card;
        }
        
        async function controlUser(username, action) {
            try {
                const response = await fetch('/api/control', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        username: username,
                        action: action
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    console.log(result.message);
                } else {
                    alert(`Error: ${result.message}`);
                }
                
            } catch (error) {
                console.error('Error controlling user:', error);
                alert('Failed to control user');
            }
        }
        
        async function startAllUsers() {
            try {
                const response = await fetch('/api/start-all', { method: 'POST' });
                const result = await response.json();
                console.log(result.message);
            } catch (error) {
                console.error('Error starting all users:', error);
                alert('Failed to start all users');
            }
        }
        
        async function stopAllUsers() {
            if (confirm('Are you sure you want to stop all user scans?')) {
                try {
                    const response = await fetch('/api/stop-all', { method: 'POST' });
                    const result = await response.json();
                    console.log(result.message);
                } catch (error) {
                    console.error('Error stopping all users:', error);
                    alert('Failed to stop all users');
                }
            }
        }
        
        async function refreshData() {
            try {
                const response = await fetch('/api/users');
                const data = await response.json();
                updateDashboard(data);
            } catch (error) {
                console.error('Error refreshing data:', error);
            }
        }
        
        // Initialize
        connectWebSocket();
        refreshData();
        
        // Refresh data every 30 seconds as backup
        setInterval(refreshData, 30000);
    </script>
</body>
</html>
    """

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the dashboard
    print("🎵 Starting MetaCrate Multi-User Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:8082")
    print("🔧 API endpoints at: http://localhost:8082/api/")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8082,
        log_level="info"
    )