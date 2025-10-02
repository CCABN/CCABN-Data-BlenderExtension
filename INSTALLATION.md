# Installation Guide

## For Blender 4.2+ / 5.x (Recommended)

### Method 1: Install from Disk

1. **Open Blender**
2. **Go to Preferences:**
   - Menu: `Edit > Preferences` (or `Blender > Preferences` on macOS)
3. **Navigate to Extensions:**
   - Click the `Extensions` tab on the left sidebar
4. **Install the Extension:**
   - Click the dropdown menu (▼) in the top-right corner
   - Select `Install from Disk...`
   - Navigate to the folder containing this extension
   - **Important:** Select the **folder itself** (not individual files)
   - Click `Install from Disk`
5. **Enable the Extension:**
   - The extension should appear in the list as "CCABN Dataset Generator"
   - Make sure the checkbox is enabled
6. **Access the Panel:**
   - Open a 3D Viewport
   - Press `N` to open the sidebar
   - Look for the `CCABN` tab

### Method 2: Install as Legacy Addon (Blender 3.x - 5.x)

1. **Create a ZIP file:**
   - Zip the entire extension folder (including all .py files and blender_manifest.toml)
   - Name it something like `ccabn_dataset_generator.zip`

2. **Install in Blender:**
   - Go to `Edit > Preferences > Add-ons`
   - Click `Install...` button
   - Select the .zip file
   - Enable "Render: CCABN Dataset Generator"

3. **Access the Panel:**
   - Open a 3D Viewport
   - Press `N` to open the sidebar
   - Look for the `CCABN` tab

## Verification

After installation, you should see:
- A new tab called "CCABN" in the 3D Viewport sidebar (press N)
- The panel titled "CCABN Dataset Generator"
- All sections: Scene Setup, Background Images, Blendshapes, Camera Variations, Light Variations, Output Settings, and Generate Dataset button

## Troubleshooting Installation

### Extension doesn't appear in the list
- Make sure you selected the folder, not individual files
- Check that `blender_manifest.toml` is in the root of the folder
- Try restarting Blender

### "Python module not found" error
- Make sure all .py files are in the same folder
- Check that `__init__.py` exists

### Panel doesn't appear in sidebar
- Press `N` in the 3D Viewport to show the sidebar
- Look for the `CCABN` tab (scroll down if needed)
- Make sure the extension is enabled in Preferences

### Legacy addon method gives errors
- Try the "Install from Disk" method instead (for Blender 4.2+)
- Make sure the zip includes all files

## Uninstallation

### Extensions Method:
1. Go to `Edit > Preferences > Extensions`
2. Find "CCABN Dataset Generator"
3. Click the dropdown (▼) next to it
4. Select `Remove`

### Legacy Addon Method:
1. Go to `Edit > Preferences > Add-ons`
2. Find "Render: CCABN Dataset Generator"
3. Click `Remove`

## System Requirements

- **Blender:** 4.2 or higher (tested on 5.x)
- **Python:** Bundled with Blender (no external installation needed)
- **GPU:** CUDA/OPTIX (NVIDIA) or HIP (AMD) for Cycles GPU rendering
- **RAM:** 4GB minimum, 8GB+ recommended for larger datasets
- **Storage:** Depends on dataset size (each 240×240 PNG is ~10-50KB)

## Next Steps

After installation, see:
- **USAGE_NOTES.md** for quick start guide
- **README.md** for full documentation
