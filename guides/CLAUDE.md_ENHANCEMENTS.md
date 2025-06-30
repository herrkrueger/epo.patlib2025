# EPO PATLIB 2025 Demo Project  
## Claude Code Enhancement of Patent Analytics

### 🎯 Project Context
Multi-stage patent analytics enhancement project for EPO PATLIB 2025 conference. Demonstrates evolution from basic patent searching to AI-enhanced strategic intelligence using numbered workflow directories.

**Original Research**: Dr. Riccardo Priore (AREA Science Park, Trieste) - PATSTAT analysis of REE patents  
**AI Enhancement**: Live Claude Code demonstration of market-correlated intelligence

### 📁 Repository Structure (Updated 2025-06-23)
```
├── 1-input/                 # Source data & original research (Riccardo's work)
├── 2-enhanced/              # Production demo system (THIS DIRECTORY)
├── 3-livedemo-template/     # Base template for new demos  
├── 4-livedemo/              # Active development environment
└── 5-archive/               # Timestamped version history
```

### 🚀 Key Workflow Components
- **Production Demos**: `2-enhanced/` - Polished notebooks for conference presentation
- **Active Development**: `4-livedemo/` - Live coding enhancements with `demo_config.json`
- **Template System**: `3-livedemo-template/` - Base for creating new demos
- **Automated Archiving**: `5-archive/` - Timestamped backups of development iterations

### ⚡ Quick Commands
```bash
# Test production system
cd 2-enhanced/utils && python -c "from demo_safety_utils import DemoSafetyManager; DemoSafetyManager().check_patstat_connection()"

# Start development session  
cd 4-livedemo && jupyter lab base_patent_notebook.ipynb

# Review configuration
cat 4-livedemo/demo_config.json | jq '.demo_info'

# Demo sequence: Market Leaders (90s) → Geographic Intelligence (90s) → Technology Network (90s)
```

### 🔧 Configuration Management (NEW)
- **Demo Config**: `4-livedemo/demo_config.json` - Comprehensive settings for live demos
  - Patent data sources (EPO OPS, Espacenet)
  - Market data integration points (JRC files)
  - Enhancement targets and priorities
  - Demo workflow phases and timing
  - IPC classification codes and REE keywords

### 🛠️ Common Issues & Solutions
- **Plotly range error**: Convert `range()` to `list(range())`
- **JSON formatting**: Validate notebook structure after programmatic creation
- **Missing imports**: Remove unused dependencies like `pycountry`
- **PATSTAT down**: Automatic fallback to demo data with clear indicators
- **Setup automation**: Run `4-livedemo/demo_setup.py` for environment preparation

### 🎭 Demo Success Factors
- **90-second timing** per notebook with live coding enhancements
- **Business value focus** - strategic insights for non-technical audience
- **Comprehensive safety** - works regardless of PATSTAT availability
- **Professional outputs** - Excel/JSON exports for follow-up
- **Automated archiving** - Development versions preserved with timestamps

### 📈 Enhancement Workflow
1. **Development**: Work in `4-livedemo/` with configuration support
2. **Testing**: Validate in `2-enhanced/` production environment
3. **Archiving**: Automatic timestamped backup to `5-archive/`
4. **Template Update**: Refresh `3-livedemo-template/` for future demos

### 📞 Future Use
This numbered workflow system is optimized for iterative patent analytics enhancement projects. See `2-enhanced/documentation/` for complete methodology and `4-livedemo/demo_config.json` for customization options.