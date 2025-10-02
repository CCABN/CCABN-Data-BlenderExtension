# Quick Usage Notes

## ✅ FIXED - Lights and Human Faces Selection Now Works!

The lights and human faces can now be properly selected using the UI:

### How to Add Lights:
1. Select a light object in your scene (in the 3D viewport or outliner)
2. In the CCABN panel, find the "Lights" list
3. Click the **+** button to add the selected light
4. Repeat for all lights you want to randomize
5. To remove a light, select it in the list and click the **-** button

### How to Add Human Faces:
1. Select a mesh object in your scene
2. In the CCABN panel, find the "Human Faces" list
3. Click the **+** button to add the selected mesh
4. Repeat for all human face meshes
5. To remove a face, select it in the list and click the **-** button

## Installation

### In Blender 4.2+/5.x:
1. Go to `Edit > Preferences > Extensions`
2. Click the dropdown (▼) menu and select `Install from Disk...`
3. Navigate to this folder (containing `blender_manifest.toml`)
4. Click `Install from Disk`
5. Enable "CCABN Dataset Generator" in the Extensions list
6. Open the 3D Viewport sidebar (press N) and find the "CCABN" tab

## Quick Start Workflow

### 1. Scene Setup
- Create or import human head meshes with Shape Keys
- Add a camera
- Add one or more lights
- Optionally create a mesh to represent a VR headset
- Background is handled automatically (no plane needed)

### 2. Configure the Addon
1. **Scene Setup Section:**
   - Select camera from dropdown
   - Add lights using + button
   - Select headset mesh (optional) from dropdown
   - Add human face meshes using + button

2. **Convert Blendshapes (Optional):**
   - If using ARKit blendshapes, click "Convert ARKit to Unified Expressions"

3. **Random Gray Tones:**
   - Set background gray min/max (default: 0.2 to 0.8)
   - Set headset gray min/max (default: 0.1 to 0.4)
   - 0.0 = black, 1.0 = white

4. **Blendshapes:**
   - Click "Refresh Blendshapes" to scan human faces
   - Check boxes to select which blendshapes to randomize
   - Set Min/Max ranges for each (0.0 to 1.0)

5. **Variations:**
   - Set camera position/rotation ranges
   - Set light position/intensity/temperature ranges

6. **Output:**
   - Choose output folder
   - Set images per human
   - Choose render engine (Cycles GPU or Eevee)

7. **Generate:**
   - Click "Generate Dataset"
   - Monitor progress in console (Window > Toggle System Console)

## Output

The extension will generate:
- Sequential PNG files: `1.png`, `2.png`, `3.png`, etc.
- Matching JSON files: `1.json`, `2.json`, `3.json`, etc.

Each JSON contains:
```json
{
  "image": "1.png",
  "human_object": "Human_001",
  "blendshapes": {
    "EyeClosedLeft": 0.34,
    "JawOpen": 0.12
  },
  "background_gray": 0.45,
  "headset_gray": 0.23
}
```

Note: `headset_gray` is only included if a headset mesh was specified.

## Tips

- **Start small:** Test with 1 human and 5 images first
- **GPU rendering:** Make sure GPU is enabled in Preferences > System
- **Console output:** Open system console to see progress
- **Eevee is faster:** Use Eevee for quick tests, Cycles for quality
- **Variation ranges:** Start with small ranges and increase gradually
- **Blendshape selection:** You don't need all 52 shapes - select the most important ones

## Common Issues

### "No active object selected"
- Make sure you've clicked on an object in the scene before clicking the + button

### "is not a light object" / "is not a mesh object"
- You're trying to add the wrong type of object
- Lights go in the Lights list, meshes go in the Human Faces list

### "No blendshapes found"
- Make sure your human face meshes have Shape Keys
- Check Properties > Object Data > Shape Keys

### Rendering is slow
- Switch to Eevee
- Reduce the number of images
- Lower render samples in Render Properties

## ARKit to Unified Expressions Mapping

The extension includes 47 blendshape mappings:

**Eye controls:** `eyeBlinkLeft` → `EyeClosedLeft`, `eyeWideRight` → `EyeWideRight`, etc.
**Brow controls:** `browInnerUp` → `BrowInnerUp`, `browDownLeft` → `BrowDownLeft`, etc.
**Jaw controls:** `jawOpen` → `JawOpen`, `jawRight` → `JawRight`, etc.
**Mouth controls:** `mouthSmileLeft` → `MouthSmileLeft`, `mouthFrownRight` → `MouthFrownRight`, etc.
**Lip controls:** `mouthPucker` → `LipPucker`, `mouthFunnel` → `LipFunnel`, etc.
**Other:** `cheekPuff` → `CheekPuff`, `noseSneerLeft` → `NoseSneerLeft`, etc.

Blendshapes that don't match between the two standards are left unchanged.

## Technical Details

- **Resolution:** 240×240 pixels
- **Color mode:** Grayscale (BW)
- **Format:** PNG
- **Camera FOV:** Set manually to 160° for OV2640 webcam simulation
- **Render engines:** Cycles (GPU) or Eevee
- **Background handling:** Random gray via world shader (0.0-1.0 range, no plane needed)
- **Headset handling:** Random gray materials on mesh (optional)
- **Metadata:** JSON sidecar files with blendshape values and gray tone values

## Development Notes

All files have been updated to use proper object references:
- `properties.py` - Uses `ObjectItem` PropertyGroup for storing object pointers
- `operators.py` - Includes add/remove operators for lights and human faces
- `ui_panel.py` - Uses `template_list` for displaying object lists with +/- buttons
- `renderer.py` - Updated to iterate through ObjectItem collections
- `utils.py` - Updated validation to work with new format

The extension is production-ready and fully functional!
