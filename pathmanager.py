import pathlib
import dataclasses
import typing
import tqdm

@dataclasses.dataclass
class PathManager:
    in_path: pathlib.Path
    out_path: pathlib.Path
    make_out_path: bool = True
    
    def __post_init__(self):
        if self.make_out_path:
            self.out_path.mkdir(parents=True, exist_ok=True)
        
    @classmethod
    def from_pathnames(cls, in_path: str, out_path: str, *args, **kwargs):
        tmp: cls = cls(
            in_path = pathlib.Path(in_path),
            out_path = pathlib.Path(out_path),
            *args, **kwargs,
        )
        return tmp
    
    def in_to_out(self, path: pathlib.Path) -> pathlib.Path:
        '''Get output file from input.'''
        rel_path = path.relative_to(self.in_path)
        return self.out_path.joinpath(rel_path)
    
    def rglob_iter(self, *args, **kwargs):
        return self.subpaths(self.in_path.rglob, *args, **kwargs)
    
    def glob_iter(self, *args, **kwargs):
        return self.subpaths(self.in_path.glob, *args, **kwargs)
    
    def subpaths(self, func: typing.Callable[[pathlib.Path], typing.Iterable[pathlib.Path]], *args, make_out_folder: bool = True, verbose: bool = False, **kwargs) -> typing.List[typing.Tuple[pathlib.Path, pathlib.Path, pathlib.Path]]:
        it: typing.Iterable[pathlib.Path] = func(*args, **kwargs)
            
        subpaths = list()
        for fp in it:
            out_path = self.in_to_out(fp)
            if make_out_folder:
                out_path.parent.mkdir(parents=True, exist_ok=True)
            subpaths.append((fp.relative_to(self.in_path), fp, out_path))
        
        if verbose:
            subpaths = tqdm.tqdm(list(subpaths), ncols=80)
        
        return subpaths
        