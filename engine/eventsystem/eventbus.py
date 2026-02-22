import weakref


class EventBus:
    def __init__(self):
        # Map eventsystem class → list of weakrefs to callback methods
        self._listeners = {}

    def subscribe(self, event_cls, callback):
        """Subscribe a method to an eventsystem. Supports automatic removal if object dies."""
        if event_cls not in self._listeners:
            self._listeners[event_cls] = []

        # Use WeakMethod if bound method, else weakref.ref for function
        if hasattr(callback, "__self__") and callback.__self__ is not None:
            ref = weakref.WeakMethod(callback)
        else:
            ref = weakref.ref(callback)

        self._listeners[event_cls].append(ref)

    def unsubscribe(self, event_cls, callback):
        if event_cls not in self._listeners:
            return
        self._listeners[event_cls] = [r for r in self._listeners[event_cls] if r() is not callback]

    def emit(self, event):
        """Call all listeners. Remove dead references automatically."""
        to_remove = []
        for ref in self._listeners.get(type(event), []):
            cb = ref()
            if cb is None:
                to_remove.append(ref)
                continue
            cb(event)
        # Clean up dead references
        for ref in to_remove:
            self._listeners[type(event)].remove(ref)
