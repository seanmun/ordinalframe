# CONTEXT.md - Ordinal Frame Project State

## 🖼️ Project Overview
**Ordinal Frame** is a Bitcoin-native digital art display built with a Raspberry Pi 5 and touchscreen. The goal is to create a minimal, forkable open-source device that displays Bitcoin Ordinals with verified ownership.

## 🎯 Current Status: Phase 1 MVP - NEARLY COMPLETE

### ✅ What's Working
- **Complete development environment** with Python 3.12.8 + Flask 3.1.1
- **GitHub repository setup** with proper dependencies and structure
- **Wallet address input** with Bitcoin address validation (all formats: legacy, segwit, taproot)
- **Hiro Ordinals API integration** - successfully fetching real Ordinals data
- **Setup page** (`/setup`) - Beautiful Bitcoin-themed interface for entering wallet address
- **Selection page** (`/select`) - Grid interface to choose which Ordinals to display
- **Server running on port 8000** (avoided port 5000 conflict)

### 🧪 Tested & Confirmed
- User successfully entered wallet address and found **4 Ordinals**
- All dependencies installed correctly
- Server running: `http://localhost:8000/setup`
- Ready to test selection interface: `http://localhost:8000/select`

---

## 🏗️ Technical Architecture

### **Tech Stack**
| Component | Technology | Status |
|-----------|------------|---------|
| Backend | Flask 3.1.1 + Python 3.12.8 | ✅ Working |
| Frontend | HTML/CSS/JavaScript | ✅ Working |
| API | Hiro Ordinals API | ✅ Integrated |
| Database | JSON files + diskcache | ✅ Implemented |
| Environment | Virtual environment (venv) | ✅ Configured |

### **Project Structure**
```
ordinalframe/
├── server.py              # Main Flask application ✅
├── templates/
│   ├── setup.html         # Wallet input page ✅
│   └── select.html        # Ordinal selection grid ✅
├── static/               # CSS, JS, assets
├── ordinals/
│   ├── cached/          # Downloaded images (auto-created)
│   └── metadata/        # JSON metadata storage
├── venv/                # Python virtual environment ✅
├── requirements.txt     # Dependencies ✅
├── .env                 # Environment config ✅
├── .gitignore          # Git ignore rules ✅
└── README.md           # Documentation ✅
```

### **Key Dependencies**
- **Flask 3.1.1** - Web framework
- **requests 2.32.3** - HTTP API calls
- **Pillow 11.2.1** - Image processing
- **diskcache 5.6.3** - Local caching
- **coloredlogs 15.0.1** - Pretty logging

---

## 🛠️ Development Setup (Completed)

### **Environment**
- **Platform**: macOS (development), Raspberry Pi 5 (target deployment)
- **Python**: 3.12.8 in virtual environment
- **Server**: Flask development server on port 8000
- **API**: Hiro Ordinals API (`https://api.hiro.so/ordinals/v1`)

### **Running the Application**
```bash
# Navigate to project
cd ordinalframe

# Activate virtual environment
source venv/bin/activate

# Start server (port 8000 to avoid conflicts)
PORT=8000 python server.py

# Access application
# Setup: http://localhost:8000/setup
# Selection: http://localhost:8000/select
# Frame: http://localhost:8000/frame (next to build)
```

---

## 📋 Current Phase Progress

### **Phase 1: Wallet Input + API Retrieval - 85% Complete**

#### ✅ Completed Components
1. **Setup Page** (`templates/setup.html`)
   - Bitcoin address validation (legacy, segwit, taproot)
   - Beautiful UI with real-time validation
   - API integration with error handling
   - Successfully tested with real wallet

2. **Flask Server** (`server.py`)
   - Complete API client for Hiro Ordinals
   - Bitcoin address validation
   - Local caching system
   - Proper error handling and logging
   - RESTful API endpoints

3. **Selection Interface** (`templates/select.html`)
   - Grid layout for Ordinal thumbnails
   - Checkbox selection system
   - "Select All/None/Rare" controls
   - Save selection functionality
   - Real metadata display

#### ⏳ Next Steps (Current Session)
4. **Enhanced Frame Display** (`templates/frame.html`)
   - Display selected Ordinals instead of samples
   - Touch interface for cycling
   - Real metadata overlays
   - Slideshow functionality

#### 🎯 API Endpoints (Implemented)
- `GET /setup` - Wallet address input page
- `GET /select` - Ordinal selection interface
- `GET /frame` - Frame display (needs enhancement)
- `POST /api/fetch-ordinals` - Fetch Ordinals for address
- `POST /api/update-selection` - Update display selection
- `GET /api/ordinals` - Get current Ordinals data
- `GET /api/health` - Health check
- `GET /content/<inscription_id>` - Proxy inscription content

---

## 🔌 API Integration Details

### **Hiro Ordinals API**
- **Base URL**: `https://api.hiro.so/ordinals/v1`
- **Endpoint**: `/inscriptions?address={address}&limit=60`
- **Authentication**: None required (public API)
- **Rate Limiting**: Handled with caching (1 hour cache)
- **Response**: Full inscription metadata including content URLs

### **Data Flow**
1. User enters Bitcoin address in setup page
2. Flask validates address format
3. Server calls Hiro API to fetch inscriptions
4. Server filters for image content types
5. Metadata stored locally in JSON
6. User selects which Ordinals to display
7. Selection saved to local JSON
8. Frame displays selected Ordinals

---

## 🎨 User Experience Flow (Current)

### **Working Flow**
1. **Visit** `http://localhost:8000/setup`
2. **Enter** Bitcoin wallet address
3. **System** validates address and fetches Ordinals
4. **Success** message shows "Found X Ordinals"
5. **Navigate** to selection page
6. **Choose** which Ordinals to display
7. **Save** selection
8. **View** frame with selected pieces

### **Tested Scenarios**
- ✅ Valid address input with 4 Ordinals found
- ✅ Address validation (format checking)
- ✅ API error handling
- ✅ Port conflict resolution (moved to 8000)

---

## 🚀 Next Session Goals

### **Immediate Tasks**
1. **Test selection page** - Verify grid display and selection saving
2. **Build enhanced frame display** - Show selected Ordinals with touch interface
3. **Test complete flow** - Setup → Select → Frame display

### **Phase 1 Completion Checklist**
- [ ] Selection page working with real thumbnails
- [ ] Frame display showing selected Ordinals
- [ ] Touch cycling between pieces
- [ ] Metadata overlay display
- [ ] Complete offline functionality

### **Phase 2 Planning**
- Bitcoin message signature verification
- Multi-wallet support
- Collection-based selection
- Advanced display modes

---

## 🐛 Known Issues & Solutions

### **Resolved Issues**
1. **Port 5000 conflict** → Solved: Using port 8000
2. **Python version mismatch** → Solved: Recreated venv with Python 3.12
3. **Flask version compatibility** → Solved: Using Flask 3.1.1
4. **Dependency installation** → Solved: All packages installed successfully

### **Current Limitations**
- Only supports image-type Ordinals (filters out text/other)
- Single wallet address per session
- No signature verification yet
- Development server only (not production-ready)

---

## 💻 Hardware Target

### **Raspberry Pi 5 Setup** (Future)
- **Board**: CanaKit Raspberry Pi 5 (8GB RAM, 128GB microSD)
- **Display**: Waveshare 10.1" Capacitive Touchscreen (1280×800)
- **Connections**: HDMI + USB for touch
- **OS**: Raspberry Pi OS with kiosk mode

### **Deployment Plan**
1. Transfer working code to Pi
2. Install dependencies
3. Configure kiosk mode (fullscreen browser)
4. Set up systemd service for auto-start
5. Configure touch interface

---

## 📚 Key Learning & Decisions

### **Architecture Decisions**
- **Flask over Django**: Simpler for embedded deployment
- **Hiro API over ord server**: Easier setup, reliable indexing
- **Local JSON over database**: Simplicity for Pi deployment
- **Virtual environment**: Proper dependency isolation

### **Development Approach**
- **Mac-first development**: Code on Mac, deploy to Pi
- **Progressive enhancement**: Basic functionality first, then polish
- **Real API integration**: No mocking, test with real data immediately

### **File Locations**
- **Main server**: `server.py` (Flask application)
- **Setup page**: `templates/setup.html` (wallet input)
- **Selection page**: `templates/select.html` (Ordinal picker)
- **Frame display**: `templates/frame.html` (display interface - needs enhancement)
- **Config**: `.env` (environment variables)
- **Dependencies**: `requirements.txt` (Python packages)

---

## 🎯 Success Metrics

### **Phase 1 Success Criteria**
- [x] User can input wallet address
- [x] System fetches real Ordinals data
- [ ] User can select which Ordinals to display (in progress)
- [ ] Frame displays selected Ordinals with touch interface
- [ ] Complete offline operation after setup

### **Demo-Ready State**
- Working wallet integration
- Beautiful selection interface
- Smooth frame display
- Touch interaction
- Ready for GitHub showcase

---

*Last Updated: Current session - Selection page created, ready to test and build frame display*