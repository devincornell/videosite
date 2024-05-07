
import pathlib
import typing
import dataclasses
import plotnine
import pandas as pd
import numpy as np

@dataclasses.dataclass
class File:
    fpath: pathlib.Path
    def __repr__(self) -> typing.Self:
        return f'{self.__class__.__name__}("{str(self.fpath)}")'
    
    @classmethod
    def get_vids_and_photos(cls, root: pathlib.Path) -> typing.List[typing.Self]:
        lglob = lambda pattern: [cls(p) for p in root.rglob(pattern)]
        return lglob('GX*.MP4') + lglob('G*.jpg')

    def number(self) -> int:
        if self.fpath.stem.startswith(f'GX'):
            return int(self.fpath.stem[2:])
        elif self.fpath.stem.startswith(f'G'):
            return int(self.fpath.stem[1:])
        else:
            raise ValueError(f'Unrecognized filename: {self.fpath.name}')


def plot_numbers(numbers: typing.Set[int]) -> plotnine.ggplot:
    '''Plot the specified numbers for continuity.'''
    return (
        plotnine.ggplot(data=presence_df(numbers))
        + plotnine.geom_line(mapping=plotnine.aes(x='range', y='present'))
    )

def presence_df(numbers: typing.Set[int]) -> pd.DataFrame:
    '''Plot the specified numbers for continuity.'''
    numbers = set(numbers)
    full = list(range(min(numbers), max(numbers)))
    return pd.DataFrame.from_dict({
        'range': full,
        'present': [int(n in numbers) for n in full],
    })

if __name__ == '__main__':
    root = pathlib.Path('/StorageDrive/raw_videos/')
    files = File.get_vids_and_photos(root)
    for file in files:
        print(file, file.number())

    numbers = [f.number() for f in files]
    df = presence_df(numbers=numbers)

    p = plot_numbers(numbers)
    (p + plotnine.theme(figure_size=(30,10))).save('results/range_plot.png', limitsize=False)



