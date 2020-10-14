from route_mapping.modules.utils.cursors.tap  import Tap

class CursorFactory:

    def getCursor(self, cursorType):
        cursorTypes = {
            'Tap': Tap
        }
        return cursorTypes[cursorType]().getCursor()