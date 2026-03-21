from engine.overlay.blockflags import BlockFlags

class Overlay:
    def __init__(self, ctx, wctx):
        self._finished = False
        self.ctx = ctx
        self.wctx = wctx

    def update(self, dt: float):
        pass

    def render(self, surf):
        pass

    def is_finished(self) -> bool:
        return self._finished

    def finish(self):
        self._finished = True

    def blocks(self) -> BlockFlags:
        """
        Return the block flags this overlay enforces.
        """
        return BlockFlags(world=True)