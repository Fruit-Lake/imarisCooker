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
        time_point = self.dataset.get('ResolutionLevel 0/TimePoint 0')
        return len(list(time_point.keys()))

    def read_channel(self, channel=0, resolution_level=0):
        """读取指定通道的图像数据

        Args:
            channel (int, optional): 通道索引，从0开始. Defaults to 0.
            resolution_level (int, optional): 分辨率级别. Defaults to 0.

        Returns:
            numpy.ndarray: 图像数据数组
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
        with tf.TiffWriter(path, bigtiff=True) as writer:
            for i in tqdm(range(self.img_shape[2]), desc=f'writing to {path}'):
                page = data[i, :self.img_shape[1], :self.img_shape[0]]
                writer.write(page, contiguous=True)

    def close(self):
        self.file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def parse_numbers(input_str: str) -> list:
    """从字符串中提取数字

    Args:
        input_str (str): 输入的字符串，数字间以逗号分隔（支持中英文逗号）

    Returns:
        list: 提取出的数字列表
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


def main():
    parser = argparse.ArgumentParser(description='IMS Reader && Converter to TIFF && Multichannel support.')
    parser.add_argument('file_path', help='IMS path')
    parser.add_argument('-save_path', help='tiff save path')
    parser.add_argument('-specify_channel', help='target channels, eg: "0,1,3"、"1,3"')

    args = parser.parse_args()
    target_channels = parse_numbers(args.specify_channel) if args.target_channel else None

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
    main()
