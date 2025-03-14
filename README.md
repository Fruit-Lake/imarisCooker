# imarisCooker

## 项目简介

imarisCooker是一个用于将Imaris软件的IMS格式文件转换为TIFF格式的工具。该工具支持多通道图像处理，可以选择性地转换特定通道的数据。

## 安装说明

### 依赖库

本工具依赖以下Python库：

```
h5py
numpy
tifffile
tqdm
argparse
```

可以使用pip安装这些依赖：

```bash
pip install h5py numpy tifffile tqdm
```

## 使用方法

### 命令行参数

```bash
python ims_to_tiff.py <file_path> [-save_path SAVE_PATH] [-specify_channel SPECIFY_CHANNEL]
```

参数说明：

- `file_path`：必需参数，指定IMS文件的路径
- `-save_path`：可选参数，指定TIFF文件的保存路径，默认为IMS文件所在目录下的`tiff`文件夹
- `-specify_channel`：可选参数，指定需要转换的通道索引，多个通道用逗号分隔，例如：0,1,3 或 1,3

### 示例

```bash
# 转换所有通道
python ims_to_tiff.py D:\data\sample.ims

# 转换指定通道并指定保存路径
python ims_to_tiff.py D:\data\sample.ims -save_path D:\output -specify_channel 0,2
```
## 注意事项

- 输入文件必须是.ims格式
- 对于大型文件，转换过程可能需要较长时间