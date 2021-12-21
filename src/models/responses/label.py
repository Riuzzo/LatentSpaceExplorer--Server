from pydantic import BaseModel
from typing import List, Optional


###############################################################################
# Models
###############################################################################


class LabelModel(BaseModel):
    columns: List[Optional[str]]
    index: List[Optional[str]]
    data: List[Optional[List]]
