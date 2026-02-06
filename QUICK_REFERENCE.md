# Quick Reference - Environment Commands

## Activate Virtual Environment
```bash
cd D:\Ginue_AI
.venv\Scripts\activate
```

## Run Backend Server
```bash
cd D:\Ginue_AI
.venv\Scripts\activate
python -m uvicorn backend.app.main:app --reload --port 8000
```

## Test Critical Packages
```bash
.venv\Scripts\python.exe -c "
import faster_whisper, mediapipe, fastapi, torch, cv2, librosa, numpy, scipy
print('✅ All packages working!')
"
```

## Check Python Version
```bash
.venv\Scripts\python.exe --version
```

## View Installed Packages
```bash
.venv\Scripts\python.exe -m pip list
```

## Install Additional Packages
```bash
.venv\Scripts\python.exe -m pip install package_name
```

## Fix DeepFace Issue (Choose One)

### Option 1: Install InsightFace (Recommended) ⭐
```bash
.venv\Scripts\python.exe -m pip install insightface
```

### Option 2: Create Python 3.13 Environment
```bash
python3.13 -m venv .venv313
.venv313\Scripts\activate
pip install -r backend/requirements.txt
```

### Option 3: Use MediaPipe Only (Already Installed)
```python
import mediapipe as mp
# No extra installation needed!
```

---

## Environment Path
- **Executable**: `D:\Ginue_AI\.venv\Scripts\python.exe`
- **VSCode Python Interpreter**: Select from `.venv\Scripts\python.exe`

## Files Generated
- `SETUP_SUMMARY.md` - Full setup report
- `DEEPFACE_FIX_GUIDE.md` - DeepFace alternatives
- `requirements_python314.txt` - Modified requirements without DeepFace
- `QUICK_REFERENCE.md` - This file

---

## Install Count Summary
✅ **95+ packages installed successfully**
❌ **DeepFace blocked** (Python 3.14 compatibility issue - see guide)

---

## Recommended Next Steps

1. **Read**: Open `SETUP_SUMMARY.md` for full details
2. **Choose**: Pick a DeepFace solution from `DEEPFACE_FIX_GUIDE.md`  
3. **Install**: Run the recommended pip install command
4. **Test**: Run "Test Critical Packages" command above
5. **Code**: Start using the environment!

---

**Status**: Environment ready for development ✅
**Issues**: Only DeepFace compatibility (4 alternative solutions provided) ⚠️
