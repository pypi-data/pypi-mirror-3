from _common import *

if has_qt4:
    from PyQt4 import QtGui, QtCore
    from PyQt4.QtCore import Qt

    import srllib.qtgui.widgets

if has_qt4:
    class _LineEdit(srllib.qtgui.widgets._LineEditHelper,
            guimocks.QLineEditMock):
        _qbase = __qbase = guimocks.QLineEditMock

        def __init__(self, contents="", undo_stack=None, undo_text=None, pos=None):
            self.__qbase.__init__(self, returnValues={"text": contents})
            srllib.qtgui.widgets._LineEditHelper.__init__(self, undo_stack,
                    undo_text, self.__qbase)
            if pos is None:
                pos = len(contents) + 1
            self.setCursorPosition(pos)

@only_qt4
class LineEditTest(QtTestCase):
    def test_construct_with_undo(self):
        """ Test constructing with undo. """
        # Test default label for undo operation
        edit, stack = self.__construct("Test", undo=True)
        edit.emit(QtCore.SIGNAL("textEdited(const QString&)"), "New")
        self.assertEqual(stack.undoText(), "edit text")

        # Test label for undo operation
        edit, stack = self.__construct("Test", undo=True, undo_text=
            "editing test")
        edit.emit(QtCore.SIGNAL("textEdited(const QString&)"), "New")
        self.assertEqual(stack.undoText(), "editing test")

    def test_undo(self):
        """ Test undo functionality. """
        edit, stack = self.__construct("Initial", undo=True)
        edit.emit(QtCore.SIGNAL("textEdited(const QString&)"), "New")
        edit.emit(QtCore.SIGNAL("textEdited(const QString&)"), "New0")
        edit.emit(QtCore.SIGNAL("editingFinished()"))
        edit.emit(QtCore.SIGNAL("textEdited(const QString&)"), "New1")
        stack.undo()
        edit.mockCheckNamedCall(self, "setText", -1, "New0")
        stack.undo()
        edit.mockCheckNamedCall(self, "setText", -1, "Initial")
        stack.redo()
        edit.mockCheckNamedCall(self, "setText", -1, "New0")
        stack.redo()
        edit.mockCheckNamedCall(self, "setText", -1, "New1")
        stack.undo()
        edit.mockCheckNamedCall(self, "setText", -1, "New0")

    def test_undo_setText(self):
        """ Test undo in conjunction with setText. """
        edit, stack = self.__construct(undo=True)
        edit.setText("Test")
        self.assertNot(stack.canUndo())
        edit.emit(QtCore.SIGNAL("textEdited(const QString&)"), "New")
        stack.undo()
        edit.mockCheckNamedCall(self, "setText", -1, "Test")

    def test_undo_setText_undoable(self):
        """ Test undo in conjunction with setText, with undoable=True. """
        edit, stack = self.__construct("Old", undo=True)
        edit.setText("New", undoable=True)
        stack.undo()
        edit.mockCheckNamedCall(self, "setText", -1, "Old")

    def test_editText_cursor(self):
        """Verify that the cursor position is kept."""
        edit, stack = self.__construct("Txt", undo=True, pos=1)
        edit.emit(QtCore.SIGNAL("textEdited(const QString&)"), "Text")
        self.assertEqual(edit.cursorPosition(), 1)

    def __construct(self, contents=None, undo=False,
            undo_text=None, pos=None):
        if contents is None:
            contents = QtCore.QString()
        if undo:
            undo_stack = QtGui.QUndoStack()
        edit = _LineEdit(contents, undo_stack=undo_stack, undo_text=undo_text,
                pos=pos)
        if not undo:
            return edit
        return edit, undo_stack

if has_qt4:
    class _NumericalLineEdit(srllib.qtgui.widgets._NumericalLineEditHelper,
        _LineEdit):
        _qbase = _LineEdit

        def __init__(self, floating_point, contents, minimum, maximum):
            self._qbase.__init__(self, contents=contents)
            srllib.qtgui.widgets._NumericalLineEditHelper.__init__(self,
                floating_point, minimum, maximum)

@only_qt4
class NumericalLineEditTest(QtTestCase):
    def test_construct(self):
        edit = self.__construct(True)
        call = edit.mockGetNamedCall("setValidator", 0)
        self.assert_(isinstance(call.args[0], QtGui.QDoubleValidator))
        edit = self.__construct(True, minimum=0, maximum=1)
        call = edit.mockGetNamedCall("setValidator", 0)
        vtor = call.args[0]
        self.assert_(isinstance(vtor, QtGui.QDoubleValidator))
        self.assertEqual(vtor.bottom(), 0)
        self.assertEqual(vtor.top(), 1)

        edit = self.__construct(False)
        call = edit.mockGetNamedCall("setValidator", 0)
        self.assert_(isinstance(call.args[0], QtGui.QIntValidator))
        edit = self.__construct(False, minimum=0, maximum=1)
        call = edit.mockGetNamedCall("setValidator", 0)
        vtor = call.args[0]
        self.assert_(isinstance(vtor, QtGui.QIntValidator))
        self.assertEqual(vtor.bottom(), 0)
        self.assertEqual(vtor.top(), 1)
        self.assertRaises(ValueError, self.__construct, False, minimum=0.1)
        self.assertRaises(ValueError, self.__construct, False, maximum=0.1)

    def __construct(self, floating_point, contents=None,
        minimum=None, maximum=None):
        if contents is None:
            contents = QtCore.QString()
        edit = _NumericalLineEdit(floating_point=
                floating_point, contents=contents, minimum=minimum, maximum=
                maximum)
        return edit

if has_qt4:
    # Note that the helper must be inherited first, to override methods in the
    # Qt base
    class _CheckBox(srllib.qtgui.widgets._CheckBoxHelper, guimocks.QCheckBoxMock):
        _qbase = guimocks.QCheckBoxMock

        def __init__(self, undo_stack=None, undo_text=None):
            guimocks.QCheckBoxMock.__init__(self)
            srllib.qtgui.widgets._CheckBoxHelper.__init__(self, undo_stack=
                undo_stack, undo_text=undo_text)

@only_qt4
class CheckBoxHelperTest(QtTestCase):
    def test_construct_with_undo(self):
        """ Test constructing with undo. """
        # Test default label for undo operation
        checkbox, stack = self.__construct(undo=True)
        self.__change_state(checkbox, True)
        self.assertEqual(stack.undoText(), "")

        # Test label for undo operation
        checkbox, stack = self.__construct(undo=True, undo_text=
            "check test")
        self.__change_state(checkbox, True)
        self.assertEqual(stack.undoText(), "check test")

    def test_undo(self):
        """ Test undo functionality. """
        checkbox, stack = self.__construct(undo=True)
        self.__change_state(checkbox, True)
        self.__change_state(checkbox, False)
        stack.undo()
        checkbox.mockCheckNamedCall(self, "setCheckState", -1, Qt.Checked)
        stack.undo()
        checkbox.mockCheckNamedCall(self, "setCheckState", -1, Qt.Unchecked)
        stack.redo()
        checkbox.mockCheckNamedCall(self, "setCheckState", -1, Qt.Checked)

    def __change_state(self, checkbox, checked):
        if checked:
            state = int(Qt.Checked)
        else:
            state = int(Qt.Unchecked)
        checkbox.emit(QtCore.SIGNAL("stateChanged(int)"), state)

    def __construct(self, checked=False, undo=False, undo_text=None):
        if undo:
            undo_stack = QtGui.QUndoStack()
        checkbox = _CheckBox(undo_stack=undo_stack, undo_text=undo_text)
        if not undo:
            return checkbox
        return checkbox, undo_stack
