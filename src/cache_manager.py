import os
import csv


class CacheManager:
    def __init__(self, out_path: str):
        print("文件将要保存到：", out_path)
        write_header = not os.path.isfile(out_path)
        self._fp = open(out_path, 'a', encoding='utf-8', newline='')
        self._writer = csv.DictWriter(self._fp, fieldnames=['name', 'value', 'frame'])
        if write_header:
            self._writer.writeheader()
        self._frame = 0          # 帧计数器

    def append(self, parameters: list[dict]):
        # parameters = [{name:..., value:...}, ...]
        self._frame += 1
        rows = [
            {"name": p["name"], "value": p["value"], "frame": self._frame}
            for p in parameters
        ]
        self._writer.writerows(rows)
        self._fp.flush()

    def close(self):
        if self._fp is None:
            return
        self._fp.close()
        self._fp = None