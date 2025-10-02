# CCABN Dataset Generator

A Blender extension for generating synthetic facial expression datasets for neural network training.

## Features

- **ARKit to Unified Expressions Conversion**: Convert blendshape naming conventions with one click
- **Randomized Dataset Generation**: Create varied facial expression images with controlled randomization
- **Configurable Variations**: Control camera position/rotation, lighting, and blendshape ranges
- **Automated Rendering**: Batch render grayscale 240×240 images with metadata
- **OV2640 Camera Simulation**: 160° field of view for realistic webcam simulation
- **GPU Acceleration**: Supports Cycles GPU and Eevee rendering

## Requirements

- Blender 4.2 or higher (tested on Blender 5.x)
- GPU with CUDA/OPTIX/HIP support (for Cycles GPU rendering)
- Human face models with Shape Keys (blendshapes)

## Installation

### Method 1: Install as Extension (Recommended for Blender 4.2+)

1. Download or clone this repository
2. In Blender, go to `Edit > Preferences > Extensions`
3. Click the dropdown menu (▼) and select `Install from Disk...`
4. Navigate to the folder containing `blender_manifest.toml`
5. Click `Install from Disk`
6. Enable the extension in the Extensions preferences

### Method 2: Install as Legacy Addon

1. Download or clone this repository
2. Zip the entire folder (including all .py files and blender_manifest.toml)
3. In Blender, go to `Edit > Preferences > Add-ons`
4. Click `Install...` and select the .zip file
5. Enable "Render: CCABN Dataset Generator"

## Setup

### 1. Prepare Your Scene

#### Human Faces
- Create or import human face models using **MPFB2** (MakeHuman Plugin for Blender)
- Optionally rig faces with **Faceit** to generate ARKit blendshapes
- Ensure each face has Shape Keys (blendshapes) for facial expressions

#### Optional Setup
- Optionally create a mesh for a VR headset (the addon will assign random gray materials)
- Background is handled automatically via world shader (no plane needed)

#### Lighting
- Add one or more light sources to your scene
- Position and configure them as desired (the addon will randomize within specified ranges)

#### Camera
- Add a camera and position it facing the human faces
- **Set the camera FOV to 160°** manually (Properties > Camera > Lens > Field of View)
  - This simulates an OV2640 webcam sensor

### 2. Using the Extension

Access the panel in the 3D Viewport sidebar under the **CCABN** tab.

#### Scene Setup
1. **Camera**: Select your scene camera from the dropdown
2. **Lights**: Select light objects in the scene and click the + button to add them to the list
3. **Headset Mesh** (Optional): Select a mesh object to represent a VR headset
4. **Human Faces**: Select mesh objects in the scene and click the + button to add them to the list

#### Convert Blendshapes (Optional)
If you used Faceit or have ARKit-named blendshapes:
1. Ensure human faces are selected/noted
2. Click **Convert ARKit to Unified Expressions**
3. The addon will rename matching blendshapes (e.g., `eyeBlinkLeft` → `EyeClosedLeft`)

#### Configure Random Gray Tones
1. **Background Gray Range**: Set min/max values (0.0 = black, 1.0 = white) for random background colors
   - Default: 0.2 to 0.8 (avoids pure black/white)
2. **Headset Gray Range**: Set min/max values for the VR headset mesh (if specified)
   - Default: 0.1 to 0.4 (darker tones typical of headsets)

#### Configure Blendshapes
1. Click **Refresh Blendshapes** to scan selected human faces
2. Use **All** / **None** to quickly select/deselect all
3. For each blendshape:
   - Check the box to include it in randomization
   - Set **Min** and **Max** values (0.0 to 1.0) for random range

#### Configure Variations

**Camera Variations:**
- **Position (±X/Y/Z)**: How far the camera can move from its base position (meters)
- **Rotation (±X/Y/Z)**: How much the camera can rotate from its base angle (degrees)

**Light Variations:**
- **Position (±X/Y/Z)**: How far lights can move from base positions (meters)
- **Intensity (Min/Max)**: Percentage of base intensity (e.g., 50% to 150%)
- **Color Temperature (Min/Max)**: Color temperature range in Kelvin (e.g., 3000K to 6500K)

#### Output Settings
1. **Output Folder**: Where to save rendered images and metadata
2. **Images per Human**: How many images to render for each face
3. **Render Engine**: Choose Cycles GPU (realistic) or Eevee (fast)

#### Generate Dataset
1. Review the **Total images** count
2. Click **Generate Dataset**
3. Monitor progress in the system console (Window > Toggle System Console on Windows)
4. Images will be saved as `1.png`, `2.png`, etc. with matching JSON metadata files

## Output Format

### Images
- Format: Grayscale PNG
- Resolution: 240×240 pixels
- Sequential numbering: `1.png`, `2.png`, `3.png`, ...

### Metadata (JSON)
Each image has a corresponding `.json` file with:
```json
{
  "image": "1.png",
  "human_object": "Human_001",
  "blendshapes": {
    "EyeClosedLeft": 0.34,
    "JawOpen": 0.12,
    "MouthSmileLeft": 0.67
  },
  "background_gray": 0.45,
  "headset_gray": 0.23
}
```

Note: `headset_gray` is only included if a headset mesh was specified.

## Workflow Example

1. Create 10 human faces in MPFB2
2. Rig each with Faceit (generates ARKit blendshapes)
3. Convert to Unified Expressions using the addon
4. Set up camera, lights, and optional headset mesh
5. Configure randomization ranges:
   - Background: 0.2-0.8 gray range
   - Headset: 0.1-0.4 gray range
   - Camera: ±0.1m position, ±5° rotation
   - Lights: ±0.2m position, 70-130% intensity, 3000-6500K temperature
   - Blendshapes: Select 20 key expressions, 0.0-1.0 range
6. Set output folder and 100 images per human
7. Click Generate Dataset
8. Wait for 1000 images to render (10 humans × 100 images)
9. Use images and metadata for neural network training

## Troubleshooting

### "No ARKit blendshapes found to convert"
- Your meshes may already use Unified Expressions naming
- Or they use a different blendshape standard (VRM, FACS, etc.)
- The conversion is optional - you can use any blendshapes

### "Object has no shape keys"
- Ensure your human face meshes have Shape Keys (blendshapes)
- In Object Mode, select the mesh and check Properties > Object Data > Shape Keys

### Rendering is slow
- Switch from Cycles to Eevee for faster rendering
- Reduce samples in render settings
- Ensure GPU rendering is enabled (Edit > Preferences > System)

### GPU not detected
- Go to Edit > Preferences > System
- Check if GPU is listed under Cycles Render Devices
- Install appropriate GPU drivers (CUDA for NVIDIA, HIP for AMD)

## Known Limitations

- Uses simple gray materials for background/headset (not photo-realistic textures)
- Camera rotation can move view away from face (user's responsibility to set appropriate ranges)
- No validation that randomized camera still frames the face
- Must add lights and human faces one at a time (no multi-select from scene)

## Future Enhancements

- Batch add multiple lights/faces from selection
- Pause/resume capability for long rendering sessions
- Preset configurations for quick setup
- Auto-detection of face in frame validation
- Support for additional blendshape standards (VRM, FACS)
- Batch export to ML-friendly formats (TFRecord, HDF5)

## License

GPL-3.0-or-later

## Credits

Created for the CCABN project for generating synthetic facial expression training data.

Uses:
- ARKit blendshape standard (Apple)
- Unified Expressions standard (VRCFaceTracking)
- Color temperature conversion algorithm (Tanner Helland)
