from pydantic import BaseModel
from resultify import resultify
import shapely as shp


class BoundingBox(BaseModel):
    """left:right  == -x:+x
    down:up == -y:+y"""

    bottom_left: tuple[float, float]
    top_right: tuple[float, float]

    def get_box_geo(self) -> shp.Polygon:
        return shp.box(*self.bottom_left, *self.top_right)

    def point_from_fractional_coordinates(self, x: float, y: float) -> shp.Point:
        """Translate fractional coordinates into coordinates withing the bounding box"""
        assert 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0, "X and Y must be fractions!"

        x_min, y_min = self.bottom_left
        x_max, y_max = self.top_right

        return shp.Point(x_min + (x_max - x_min) * x, y_min + (y_max - y_min) * y)

    @resultify(Exception)
    def fractional_coordinates_from_point(
        self, point: shp.Point
    ) -> tuple[float, float]:
        box = self.get_box_geo()
        if not box.contains(point):
            raise Exception(f"Point {point} is not within the bounding box {box}")

        x, y = point.x, point.y
        x_min, y_min = self.bottom_left
        x_max, y_max = self.top_right
        return ((x - x_min) / (x_max - x_min), (y - y_min) / (y_max - y_min))


class StaticAreaDetails(BaseModel):
    name: str
    description: str
    bounding_rectangle: BoundingBox
    """Area of interest bounding box"""
    grid_cell_counts: tuple[int, int]
    """Cell counts. Vertically and Horizontally. Must match 
    the final model input! For poland 64x64 grid gives 10km cell 
    size which is about square. Poland is a fairly square country..."""
