import pygame


class LineSegment:
    def __init__(self, p1: tuple[int, int], p2: tuple[int, int]):
        """
        Represents a simple line segment from point p1 to point p2.
        p1, p2: tuple or pygame.Vector2
        """
        self.p1 = pygame.Vector2(p1)
        self.p2 = pygame.Vector2(p2)

    def contains_x(self, x: float) -> bool:
        """Return True if x is within the horizontal bounds of the segment."""
        return min(self.p1.x, self.p2.x) <= x <= max(self.p1.x, self.p2.x)

    def y_at_x(self, x: float) -> float:
        """
        Returns the y-coordinate on the line at a given x.
        Assumes x is within the segment's range (you should call contains_x() first).
        """
        dx = self.p2.x - self.p1.x
        dy = self.p2.y - self.p1.y

        # Handle near-vertical lines more safely
        if abs(dx) < 1e-6:  # very small threshold
            return (self.p1.y + self.p2.y) / 2  # or just self.p1.y — your choice

        t = (x - self.p1.x) / dx  # parametric [0..1]
        return self.p1.y + t * dy

    def render(self, surf: pygame.Surface, color=(255, 0, 0), width=1, offset=(0, 0)):
        pygame.draw.line(
            surf,
            color,
            (self.p1.x - offset[0], self.p1.y - offset[1]),
            (self.p2.x - offset[0], self.p2.y - offset[1])
        )
