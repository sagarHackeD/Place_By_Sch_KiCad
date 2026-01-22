"""MaxRects bin packing algorithm implementation."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Rect:
    x: int
    y: int
    w: int
    h: int


class MaxRectsBin:
    def __init__(self, width: int, height: int, allow_rotate: bool = False):
        self.width = width
        self.height = height
        self.allow_rotate = allow_rotate
        self.free_rects = [Rect(0, 0, width, height)]
        self.used_rects = []

    def insert(self, w: int, h: int) -> Optional[Rect]:
        best_rect = None
        best_score = float("inf")

        for free in self.free_rects:
            # No rotation
            if w <= free.w and h <= free.h:
                score = free.w * free.h - w * h
                if score < best_score:
                    best_score = score
                    best_rect = Rect(free.x, free.y, w, h)

            # With rotation
            if self.allow_rotate and h <= free.w and w <= free.h:
                score = free.w * free.h - w * h
                if score < best_score:
                    best_score = score
                    best_rect = Rect(free.x, free.y, h, w)

        if best_rect is None:
            return None

        self._place_rect(best_rect)
        return best_rect

    def _place_rect(self, rect: Rect):
        i = 0
        while i < len(self.free_rects):
            if self._intersects(rect, self.free_rects[i]):
                self._split_free_rect(self.free_rects[i], rect)
                self.free_rects.pop(i)
            else:
                i += 1

        self._prune_free_list()
        self.used_rects.append(rect)

    def _split_free_rect(self, free: Rect, used: Rect):
        if used.x > free.x:
            self.free_rects.append(Rect(free.x, free.y, used.x - free.x, free.h))

        if used.x + used.w < free.x + free.w:
            self.free_rects.append(
                Rect(
                    used.x + used.w, free.y, free.x + free.w - (used.x + used.w), free.h
                )
            )

        if used.y > free.y:
            self.free_rects.append(Rect(free.x, free.y, free.w, used.y - free.y))

        if used.y + used.h < free.y + free.h:
            self.free_rects.append(
                Rect(
                    free.x, used.y + used.h, free.w, free.y + free.h - (used.y + used.h)
                )
            )

    def _prune_free_list(self):
        i = 0
        while i < len(self.free_rects):
            j = i + 1
            while j < len(self.free_rects):
                if self._contains(self.free_rects[i], self.free_rects[j]):
                    self.free_rects.pop(j)
                elif self._contains(self.free_rects[j], self.free_rects[i]):
                    self.free_rects.pop(i)
                    i -= 1
                    break
                else:
                    j += 1
            i += 1

    @staticmethod
    def _intersects(a: Rect, b: Rect) -> bool:
        return not (
            a.x + a.w <= b.x or a.x >= b.x + b.w or a.y + a.h <= b.y or a.y >= b.y + b.h
        )

    @staticmethod
    def _contains(a: Rect, b: Rect) -> bool:
        return (
            b.x >= a.x
            and b.y >= a.y
            and b.x + b.w <= a.x + a.w
            and b.y + b.h <= a.y + a.h
        )
