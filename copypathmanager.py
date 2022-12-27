import pathlib
import dataclasses
import typing
import tqdm

@dataclasses.dataclass(order=True, frozen=True)
class PathEntry:
    in_path: pathlib.Path
    new_path: pathlib.Path
    rel_path: pathlib.Path
    
    @property
    def name(self) -> str:
        return self.in_path.stem.replace('_', ' ')

@dataclasses.dataclass
class CopyPathManager:
    in_path: pathlib.Path
    out_path: pathlib.Path
    patterns: typing.List[str] = dataclasses.field(default_factory=lambda: ['*'])
    make_out_path: bool = False
    
    def __post_init__(self):
        if self.make_out_path:
            self.out_path.mkdir(parents=True, exist_ok=True)
    
    ###################### Constructors ######################    
    @classmethod
    def from_pathnames(cls, in_path: str, out_path: str, *args, **kwargs):
        tmp: cls = cls(
            in_path = pathlib.Path(in_path),
            out_path = pathlib.Path(out_path),
            *args, **kwargs,
        )
        return tmp
    
        
    ###################### For globbing ######################
    def glob_iter(self, patterns: typing.List[str] = None, *args, **kwargs):
        return self.subpath_patterns(self.in_path.glob, patterns, *args, **kwargs)
    
    def rglob_iter(self, patterns: typing.List[str] = None, *args, **kwargs):
        return self.subpath_patterns(self.in_path.rglob, patterns, *args, **kwargs)
    
    def subpath_patterns(self, func: typing.Callable[[pathlib.Path], typing.Iterable[pathlib.Path]], patterns: typing.List[str], *args, verbose: bool = False, **kwargs) -> typing.List[PathEntry]:
        if patterns is None:
            patterns = self.patterns
        
        if isinstance(patterns, str):
            raise TypeError('pattern should be a list of string patterns, not a string.')
        
        subpaths = list()
        for pattern in patterns:
            subpaths += self.subpaths(func, pattern, *args, **kwargs)
        
        subpaths = list(sorted(subpaths))
        if verbose:
            subpaths = tqdm.tqdm(subpaths, ncols=80)
        
        return subpaths
    
    def subpaths(self, func: typing.Callable[[pathlib.Path], typing.Iterable[pathlib.Path]], *args, make_new_folder: bool = False, **kwargs) -> typing.List[PathEntry]:
        it: typing.Iterable[pathlib.Path] = func(*args, **kwargs)
            
        subpaths = list()
        for fp in it:
            out_path = self.in_to_out(fp)
            if make_new_folder or self.make_out_path:
                out_path.parent.mkdir(parents=True, exist_ok=True)
            subpaths.append(PathEntry(
                rel_path = fp.relative_to(self.in_path), 
                in_path = fp, 
                new_path = out_path,
            ))
                
        return subpaths
    
    ###################### Path Conversions ######################
    def in_to_out(self, path: pathlib.Path) -> pathlib.Path:
        '''Get output file from input.'''
        rel_path = path.relative_to(self.in_path)
        return self.out_path.joinpath(rel_path)

    
    
    