from pydantic import BaseModel


###############################################################################
# Models
###############################################################################


class ImagesFolderModel(BaseModel):
    images_folder_name: str
