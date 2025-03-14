# _*_ coding: utf-8 _*_
# @Time    : 2025/3/14 9:52
# @Author  : Guanhao Sun
# @File    : ims_to_tiff.py
# @IDE     : PyCharm
import os
import h5py
import numpy as np
import tifffile as tf
from tqdm import tqdm
import argparse


class IMSReader:
    """IMS文件读取器，用于读取和处理IMS格式的图像文件。

    该类提供了读取IMS文件、获取图像信息以及将图像数据转换为TIFF格式的功能。

    Attributes:
        file_path (str): IMS文件的路径
        save_path (str): TIFF文件的保存路径
        dirname (str): IMS文件所在目录
        basename (str): IMS文件名（包含扩展名）
        name (str): IMS文件名（不含扩展名）
        file (h5py.File): 打开的HDF5文件对象
        dataset: 数据集对象
        dataset_info: 数据集信息对象
        img_attrs: 图像属性
        img_shape (numpy.ndarray): 图像形状 [X, Y, Z]
        channels (int): 图像通道数

    Example:
        >>> with IMSReader('sample.ims') as reader:
        ...     data = reader.read_channel(0)
        ...     reader.write_to_tiff(data, 'output.tiff')
    """
    def __init__(self, file_path, save_path: str = None):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'文件不存在：{file_path}')
        if not file_path.endswith('.ims'):
            raise ValueError('输入文件必须是.ims格式')

        self.file_path = file_path
        self.dirname = os.path.dirname(file_path)
        if save_path is None:
            self.save_path = self.dirname + '\\tiff'
        else:
            self.save_path = save_path
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        self.basename = os.path.basename(file_path)
        self.name = os.path.splitext(self.basename)[0]

        self.file = h5py.File(file_path, 'r')
        self.dataset = self.file.get('DataSet')
        self.dataset_info = self.file.get('DataSetInfo')
        self.img_attrs = self.dataset_info.get('Image').attrs

        self.img_shape = self.get_img_shape()
        self.channels = self.get_channel_count()

    def get_img_shape(self):
        """获取图像的形状信息。

        从图像属性中提取X、Y、Z维度的信息，并将其转换为整数数组。

        Returns:
            numpy.ndarray: 包含图像X、Y、Z维度大小的数组
        """
        queue = [
            np.array(self.img_attrs['X'], dtype=int),
            np.array(self.img_attrs['Y'], dtype=int),
            np.array(self.img_attrs['Z'], dtype=int)
        ]

        out = []
        for q in queue:
            temp = 0
            c = 1
            for i in np.flip(q, axis=0):
                temp += i * c
                c *= 10
            out.append(temp)
        return np.array(out, dtype=int)

    def get_channel_count(self):
        """获取图像的通道数。

        Returns:
            int: 图像的通道数量
        """
        time_point = self.dataset.get('ResolutionLevel 0/TimePoint 0')
        return len(list(time_point.keys()))

    def read_channel(self, channel=0, resolution_level=0):
        """读取指定通道的图像数据。

        Args:
            channel (int, optional): 通道索引，从0开始. Defaults to 0.
            resolution_level (int, optional): 分辨率级别，0表示原始分辨率. Defaults to 0.

        Returns:
            numpy.ndarray: 图像数据数组

        Raises:
            ValueError: 当指定的分辨率级别或通道不存在时抛出
        """
        res_path = f'ResolutionLevel {resolution_level}'
        if res_path not in self.dataset:
            raise ValueError(f'不支持的分辨率级别：{resolution_level}')

        resolution = self.dataset.get(res_path)
        time_point = resolution.get('TimePoint 0')
        channel_path = f'Channel {channel}'

        if channel_path not in time_point:
            raise ValueError(f'通道{channel}不存在')

        channel_data = time_point.get(channel_path)
        return np.array(channel_data.get('Data'))

    def write_to_tiff(self, data, path):
        """将图像数据写入TIFF文件。

        Args:
            data (numpy.ndarray): 要写入的图像数据
            path (str): TIFF文件的保存路径

        Note:
            使用bigtiff格式保存，支持大于4GB的文件
        """
        with tf.TiffWriter(path, bigtiff=True) as writer:
            for i in tqdm(range(self.img_shape[2]), desc=f'writing to {path}'):
                page = data[i, :self.img_shape[1], :self.img_shape[0]]
                writer.write(page, contiguous=True)

    def close(self):
        """关闭文件对象。

        在使用完IMSReader后应调用此方法释放资源。
        """
        self.file.close()

    def __enter__(self):
        """上下文管理器入口。

        Returns:
            IMSReader: 返回IMSReader实例自身
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口。

        在退出上下文时自动关闭文件。

        Args:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常追踪信息
        """
        self.close()


def parse_numbers(input_str: str) -> list:
    """从字符串中提取数字

    Args:
        input_str (str): 输入的字符串，数字间以逗号分隔（支持中英文逗号）

    Returns:
        list: 提取出的数字列表

    Raises:
        ValueError: 当输入字符串包含非数字内容时抛出
    """
    # 将中文逗号替换为英文逗号
    input_str = input_str.replace('，', ',')
    # 分割字符串并过滤空值
    numbers = [num.strip() for num in input_str.split(',') if num.strip()]
    # 转换为整数
    try:
        return [int(num) for num in numbers]
    except ValueError:
        raise ValueError('输入的字符串包含非数字内容')


def convert_ims_to_tiff(file_path: str, save_path: str = None, specify_channels: list = None) -> list:
    """将IMS文件转换为TIFF格式

    将指定的IMS文件转换为TIFF格式，可以选择性地转换特定通道。
    如果未指定保存路径，将在IMS文件所在目录下创建tiff子目录保存转换后的文件。

    Args:
        file_path (str): IMS文件路径
        save_path (str, optional): TIFF文件保存路径. Defaults to None.
        specify_channels (list, optional): 指定要转换的通道列表，例如[0,1,3]. Defaults to None.

    Returns:
        list: 转换后的TIFF文件路径列表

    Example:
        >>> files = convert_ims_to_tiff('sample.ims', specify_channels=[0, 1])
        >>> print(files)
        ['path/to/sample_C0.tiff', 'path/to/sample_C1.tiff']
    """
    output_files = []
    with IMSReader(file_path, save_path) as reader:
        for i in range(reader.channels):
            if specify_channels is None or i in specify_channels:
                print(f'reading channel {i + 1}')
                data = reader.read_channel(i)
                if reader.channels != 1:
                    save_path = f'{reader.save_path}\\{reader.name}_c{i + 1}.tiff'
                else:
                    save_path = f'{reader.save_path}\\{reader.name}.tiff'
                reader.write_to_tiff(data, save_path)
                output_files.append(save_path)
    return output_files


def cli_main():
    """命令行接口主函数

    处理命令行参数并执行IMS到TIFF的转换操作。支持以下参数：
    - file_path: IMS文件路径
    - save_path: 保存路径（可选）
    - channels: 要转换的通道列表（可选）

    Example:
        $ python ims_to_tiff.py sample.ims --save_path ./output --channels 0,1,2
    """
    parser = argparse.ArgumentParser(description='IMS Reader && Converter to TIFF && Multichannel support.')
    parser.add_argument('file_path', help='IMS path')
    parser.add_argument('-save_path', help='tiff save path')
    parser.add_argument('-specify_channel', help='target channels, eg: "0,1,3"、"1,3"')

    args = parser.parse_args()
    target_channels = parse_numbers(args.specify_channel) if args.specify_channel else None

    with IMSReader(args.file_path) as reader:
        for i in range(reader.channels):
            if target_channels is None or i in target_channels:
                print(f'reading channel {i + 1}')
                data = reader.read_channel(i)
                if reader.channels != 1:
                    save_path = f'{reader.save_path}\\{reader.name}_c{i + 1}.tiff'
                else:
                    save_path = f'{reader.save_path}\\{reader.name}.tiff'
                reader.write_to_tiff(data, save_path)


if __name__ == '__main__':
    cli_main()