class OverlayManager:
    def __init__(self, ctx, wctx):
        self.ctx = ctx
        self.wctx = wctx
        self.stack = []

    def push(self, overlay):
        self.stack.append(overlay)

    def update(self, dt):
        if not self.stack:
            return

        top = self.stack[-1]
        top.update(dt)

        if top.is_finished():
            self.stack.pop()

    def render(self, surf):
        for o in self.stack:
            o.render(surf)

    def flush(self):
        self.stack.clear()

    def blocks_world_update(self) -> bool:
        return self.stack and self.stack[-1].blocks_world()