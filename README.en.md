# imarisCooker

## Introduction

imarisCooker is a specialized tool designed for converting Imaris software's IMS format files to TIFF format. This tool supports multi-channel image processing and allows selective conversion of specific channels.

## Installation

```bash
pip install imaris-cooker
```

## Usage

### Command Line Interface

```bash
# bash
imaris-cooker <file_path> [-save_path SAVE_PATH] [-specify_channel SPECIFY_CHANNEL]
```

### Python API
```python
# python
import imaris_cooker
file_path = 'your .ims file path'
save_path = 'export .tiff file path'
specify_channel = [0,2] # specify channel index, None to extract all channels
imaris_cooker.convert_ims_to_tiff(file_path, save_path, specify_channel)
```

Parameters:

- `file_path`: Required parameter, specifies the path to the IMS file
- `-save_path`: Optional parameter, specifies the save path for the TIFF file (defaults to a 'tiff' folder in the same directory as the IMS file)
- `-specify_channel`: Optional parameter, specifies the channel indices to convert, multiple channels should be comma-separated (e.g., 0,1,3 or 1,3)

### Examples

```bash
# bash
# Convert all channels
imaris-cooker D:\data\sample.ims

# Convert specific channels with custom save path
imaris-cooker D:\data\sample.ims -save_path D:\output -specify_channel 0,2
```

```python
# python
import imaris_cooker

# Convert all channels
imaris_cooker.convert_ims_to_tiff(r'D:\data\sample.ims')

# Convert specific channels with custom save path
imaris_cooker.convert_ims_to_tiff(r'D:\data\sample.ims', r'D:\data\out', [0, 2])
```

## Important Notes

- Input files must be in .ims format
- Converting large files may take considerable time