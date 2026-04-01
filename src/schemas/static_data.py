from pydantic import BaseModel
import shapely as shp

class BoundingBox(BaseModel):
    bottom_left: tuple[float, float]
    top_right: tuple[float, float]

    def get_box_geo(self) -> shp.Polygon:
        return shp.box(*self.bottom_left, *self.top_right)

class StaticAreaDetails:
    name: str
    description: str
    bounding_rectangle: BoundingBox
    """Area of interest bounding box"""
    grid_cell_counts: tuple[int, int]
    """Cell counts. Vertically and Horizontally. Must match 
    the final model input! For poland 64x64 grid gives 10km cell 
    size which is about square. Poland is a fairly square country..."""
