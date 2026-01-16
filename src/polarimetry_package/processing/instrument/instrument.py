from dataclasses import dataclass
from pathlib import Path
from typing import Self

@dataclass(frozen=True)
class InstrumentModel:
    file_directry: str
    suffix:str
    extension: str 
    
    @classmethod
    def load(cls, file_directry, suffix="", extension="") -> Self:
        return cls(
                file_directry= file_directry,
                suffix= suffix,
                extension= extension,
                )

    @staticmethod
    def get_path_list(file_directry: str, suffix: str, extension: str) -> list[Path]:
        path = Path(file_directry)
        pattern = f"*{suffix}{extension}"
        path_list = list(path.glob(pattern))
        return path_list

    def path_list(self) -> list:
        return self.get_path_list(
                                file_directry= self.file_directry,
                                suffix= self.suffix,
                                extension=self.extension
                                )
#ImageSetへ移植済み(2026.1.8)
#    def load(self):
#        path_list = self.path_list()
#        data, hdr_profile = reader.load_data(path_list)
#
#        return ImageSet(data= data, noise= None, 
#                        hdr_profile= hdr_profile,
#                        status={}, status_keyword={"POL0":{},"POL60":{},"POL120":{}}) 
