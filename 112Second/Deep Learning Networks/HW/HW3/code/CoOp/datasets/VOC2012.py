import os
from dassl.data.datasets import DATASET_REGISTRY, DatasetBase, Datum

@DATASET_REGISTRY.register()
class VOC2012(DatasetBase):
    dataset_dir = "VOCtrainval_11-May-2012"

    def __init__(self, cfg):
        root = os.path.abspath(os.path.expanduser(cfg.DATASET.ROOT))
        self.dataset_dir = os.path.join(root, 'VOCdevkit', 'VOC2012')
        train_split = os.path.join(self.dataset_dir, 'ImageSets', 'Main', 'train.txt')
        val_split = os.path.join(self.dataset_dir, 'ImageSets', 'Main', 'val.txt')
        test_split = os.path.join(self.dataset_dir, 'ImageSets', 'Main', 'test.txt')

        train = self._read_split(train_split)
        val = self._read_split(val_split)
        test = self._read_split(test_split)

        super().__init__(train_x=train, val=val, test=test)

    def _read_split(self, split_file):
        items = []
        with open(split_file, 'r') as f:
            lines = f.readlines()
        for line in lines:
            impath = os.path.join(self.dataset_dir, 'JPEGImages', f"{line.strip()}.jpg")
            items.append(Datum(impath=impath, label=0))  # 需要根据实际标签进行调整
        return items
