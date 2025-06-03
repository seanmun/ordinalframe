# 🖼️ Ordinal Frame

A Bitcoin-native digital art display that verifies ownership and displays your Ordinals collection on a touchscreen frame.

![Bitcoin](https://img.shields.io/badge/Bitcoin-F7931A?style=for-the-badge&logo=bitcoin&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1.1-green?style=for-the-badge&logo=flask)
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-A22846?style=for-the-badge&logo=Raspberry%20Pi&logoColor=white)

## Why This Exists

Unlike NFTs that rely on off-chain metadata, **Bitcoin Ordinals are inscribed directly on-chain**, making them permanent and truly decentralized. This frame celebrates that permanence by providing a dedicated, always-on display for your collection.

Perfect for showcasing your Quantum Cats, rare sats, inscribed art, and any other Bitcoin-native digital assets.

## ✨ Features

- 🔗 **Wallet Integration** - Enter your Bitcoin address to fetch your Ordinals
- 🎨 **Smart Content Support** - Displays images, HTML, and interactive inscriptions
- 📱 **Touch Interface** - Tap to cycle, long-press for metadata
- 🔄 **Auto Slideshow** - Cycles through your collection automatically
- 📊 **Rich Metadata** - Shows inscription numbers, rarity, collection info
- 💾 **Offline Operation** - Works without internet after initial setup
- 🖥️ **Kiosk Mode Ready** - Perfect for Raspberry Pi deployment
- 🐱 **Quantum Cat Compatible** - Properly renders interactive HTML inscriptions

## 🚀 Quick Start

### Mac/PC Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/ordinal-frame.git
   cd ordinal-frame
   ```

2. **Run the setup script:**
   ```bash
   chmod +x setup-repo.sh
   ./setup-repo.sh
   ```

3. **Start the server:**
   ```bash
   source venv/bin/activate
   PORT=8000 python server.py
   ```

4. **Open your browser:**
   - Setup: http://localhost:8000/setup
   - Selection: http://localhost:8000/select  
   - Frame: http://localhost:8000/frame

### First Time Setup

1. **Enter your Bitcoin address** on the setup page
2. **Select which Ordinals to display** from your collection
3. **Enjoy your personalized frame** cycling through your chosen pieces

## 🛠️ Hardware (Raspberry Pi Deployment)

### Recommended Hardware

- **Raspberry Pi 5** (8GB RAM recommended)
- **Waveshare 10.1" Capacitive Touchscreen** (1280×800)
- **128GB+ microSD card** (Class 10 or better)
- **Official Raspberry Pi power supply**

### Connections

- **HDMI**: Pi to screen for display
- **USB**: Pi to screen for touch input
- **Power**: Official power supply for stable operation

## 🎮 Interface

### Touch Controls

- **Single Tap**: Cycle to next Ordinal
- **Long Press**: Show/hide metadata overlay
- **Navigation Dots**: Jump to specific Ordinal

### Keyboard Controls (Development)

- **Space/Right Arrow**: Next Ordinal
- **Left Arrow**: Previous Ordinal
- **I**: Toggle metadata info
- **P**: Pause/resume slideshow

## 🏗️ Architecture

### Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Backend | Flask 3.1.1 | Web server and API |
| Frontend | HTML/CSS/JavaScript | Touch-optimized interface |
| Bitcoin API | Hiro Ordinals API | Fetch inscription data |
| Storage | JSON + File Cache | Local data and images |
| Deployment | Raspberry Pi OS | Kiosk mode display |

### Project Structure

```
ordinal-frame/
├── server.py              # Main Flask application
├── templates/             # HTML interface templates
│   ├── setup.html         # Wallet address input
│   ├── select.html        # Ordinal selection grid
│   └── frame.html         # Main display interface
├── static/               # CSS, JS, and static assets
├── ordinals/             # Ordinal data and cache
│   ├── cached/          # Downloaded inscription images
│   └── metadata/        # JSON metadata storage
├── requirements.txt      # Python dependencies
├── .env                 # Environment configuration
└── README.md            # This file
```

## 🔌 API Integration

### Supported APIs

- **Primary**: [Hiro Ordinals API](https://docs.hiro.so/ordinals) - Reliable, fast, free
- **Backup**: Direct Bitcoin Core integration (advanced)

### Data Flow

1. User enters Bitcoin wallet address
2. System validates address format
3. Fetch inscriptions from Hiro API
4. Filter and cache inscription data
5. User selects which Ordinals to display
6. Frame cycles through selected pieces

## 🎨 Supported Content Types

- ✅ **Images**: PNG, JPEG, GIF, WebP, SVG
- ✅ **Interactive HTML**: Quantum Cats, generative art
- ✅ **Text**: Plain text inscriptions
- 🔄 **Future**: Audio, video, and other formats

## 📊 Demo Data

The frame has been tested with:
- **6 real Ordinals** from live Bitcoin wallet
- **Mixed content types** (images + HTML)
- **Quantum Cats** (interactive inscriptions)
- **Various inscription numbers** (early and recent)

## 🚧 Development

### Running Tests

```bash
source venv/bin/activate
pytest tests/
```

### Code Formatting

```bash
black *.py
flake8 *.py
```

### Environment Variables

Key settings in `.env`:
- `PORT=8000` - Server port
- `HIRO_API_BASE_URL` - Ordinals API endpoint
- `DEFAULT_SLIDESHOW_INTERVAL=30` - Seconds between slides

## 🔮 Roadmap

### ✅ Phase 1 - Basic Display (Complete)
- [x] Wallet address input and validation
- [x] Ordinals API integration
- [x] Selection interface with thumbnails
- [x] Touch-optimized frame display
- [x] Support for images and HTML content
- [x] Metadata overlays and navigation

### 🔄 Phase 2 - Ownership Verification (Next)
- [ ] Bitcoin message signing for ownership proof
- [ ] Multi-wallet support
- [ ] Collection-based filtering
- [ ] Enhanced security features

### 🔮 Phase 3 - Advanced Features (Future)
- [ ] Multiple display modes (grid, slideshow, focus)
- [ ] Custom themes and styling
- [ ] Social sharing integration
- [ ] Remote management interface

### 🥧 Phase 4 - Hardware Optimization (Future)
- [ ] One-click Pi deployment
- [ ] Hardware performance optimization
- [ ] Power management features
- [ ] Physical frame mounting guides

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes with proper tests
4. Format code: `make format`
5. Run tests: `make test`
6. Submit a pull request

### Development Guidelines

- **Bitcoin-first**: Always prioritize Bitcoin-native solutions
- **Simplicity**: Keep dependencies minimal for Pi deployment
- **Privacy**: Never store private keys or sensitive data
- **Offline-capable**: Core features must work without internet

## 🔒 Security & Privacy

- **No private keys**: Only public addresses are used
- **Local storage**: All data cached locally on device
- **API proxy**: Content served through local server
- **No tracking**: No analytics or user tracking

## 🐛 Known Limitations

- **Content dependencies**: Some HTML inscriptions need external resources
- **Single wallet**: Currently supports one wallet at a time
- **No signature verification**: Phase 1 uses address-based fetching only
- **Development server**: Not optimized for production deployment yet

## 📚 Resources

### Bitcoin Ordinals
- [Ordinals Theory Handbook](https://docs.ordinals.com/)
- [Hiro Ordinals API](https://docs.hiro.so/ordinals)
- [Bitcoin Core](https://bitcoincore.org/)

### Hardware Setup
- [Raspberry Pi Documentation](https://www.raspberrypi.org/documentation/)
- [Waveshare Touchscreen Guide](https://www.waveshare.com/wiki/10.1inch_HDMI_LCD)

## 🙏 Acknowledgments

- **Bitcoin Core Developers** - For building the foundation
- **Ordinals Protocol** - For bringing digital artifacts to Bitcoin
- **Hiro Systems** - For providing reliable Ordinals API
- **Raspberry Pi Foundation** - For accessible computing hardware
- **Open Source Community** - For tools and inspiration

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🎯 Perfect For

- **Bitcoin Art Collectors** - Showcase your Ordinals collection
- **Galleries & Exhibitions** - Display Bitcoin-native art
- **Developers** - Learn Bitcoin + Ordinals integration
- **Educators** - Demonstrate blockchain permanence
- **Enthusiasts** - Cool project for your home/office

---

Built with ❤️ for the Bitcoin community.

**Ready to display your Ordinals?** Star this repo and build your own frame! 🖼️✨