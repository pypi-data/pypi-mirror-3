#ifndef __PYX_HAVE__elementary__c_elementary
#define __PYX_HAVE__elementary__c_elementary

struct PyElementaryObject;
struct PyElementaryGestureLayer;
struct PyElementaryLayout;
struct PyElementaryImage;
struct PyElementaryButton;
struct PyElementaryWindow;
struct PyElementaryStandardWindow;
struct PyElementaryInnerWindow;
struct PyElementaryBackground;
struct PyElementaryIcon;
struct PyElementaryBox;
struct PyElementaryFrame;
struct PyElementaryFlip;
struct PyElementaryScroller;
struct PyElementaryLabel;
struct PyElementaryTable;
struct PyElementaryClock;
struct PyElementaryHover;
struct PyElementaryEntry;
struct PyElementaryBubble;
struct PyElementaryPhoto;
struct PyElementaryHoversel;
struct PyElementaryToolbar;
struct PyElementaryList;
struct PyElementarySlider;
struct PyElementaryNaviframe;
struct PyElementaryRadio;
struct PyElementaryCheck;
struct PyElementaryGenlist;
struct PyElementaryGengrid;
struct PyElementarySpinner;
struct PyElementaryNotify;
struct PyElementaryFileselector;
struct PyElementaryFileselectorEntry;
struct PyElementaryFileselectorButton;
struct PyElementarySeparator;
struct PyElementaryProgressbar;
struct PyElementaryMenu;
struct PyElementaryPanel;
struct PyElementaryWeb;
struct PyElementaryActionslider;
struct PyElementaryCalendar;
struct PyElementaryColorselector;
struct PyElementaryIndex;
struct PyElementaryCtxpopup;
struct PyElementaryGrid;
struct PyElementaryVideo;
struct PyElementaryPlayer;
struct PyElementaryConformant;
struct PyElementaryDayselector;
struct PyElementaryPanes;
struct PyElementaryThumb;
struct PyElementaryDiskselector;
struct PyElementaryDatetime;
struct PyElementaryMap;
struct PyElementaryMapbuf;
struct PyElementaryMultiButtonEntry;
struct PyElementarySlideshow;
struct PyElementarySegmentControl;
struct PyElementaryPopup;
struct PyElementaryPlug;
struct PyElementaryPhotocam;
struct PyElementaryFlipSelector;

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_object.pxi":134
 *         pass
 * 
 * cdef public class Object(evasObject) [object PyElementaryObject, type PyElementaryObject_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """An abstract class to manage object and callback handling.
 */
struct PyElementaryObject {
  struct PyEvasObject __pyx_base;
  PyObject *_elmcallbacks;
  PyObject *_elm_event_cbs;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_gesture_layer.pxi":32
 *         traceback.print_exc()
 * 
 * cdef public class GestureLayer(Object) [object PyElementaryGestureLayer, type PyElementaryGestureLayer_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """Use Gesture Layer to detect gestures. The advantage is that you don't
 */
struct PyElementaryGestureLayer {
  struct PyElementaryObject __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_layout.pxi":19
 * #
 * 
 * cdef public class Layout(LayoutClass) [object PyElementaryLayout, type PyElementaryLayout_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """This is a container widget that takes a standard Edje design file and
 */
struct PyElementaryLayout {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};
struct PyElementaryImage {
  struct PyElementaryObject __pyx_base;
};
struct PyElementaryButton {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_window.pxi":23
 * from evas.c_evas cimport Canvas_from_instance
 * 
 * cdef public class Window(Object) [object PyElementaryWindow, type PyElementaryWindow_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """The window class of Elementary.
 */
struct PyElementaryWindow {
  struct PyElementaryObject __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_window.pxi":1717
 * _install_metaclass(&PyElementaryWindow_Type, ElementaryObjectMeta)
 * 
 * cdef public class StandardWindow(Window) [object PyElementaryStandardWindow, type PyElementaryStandardWindow_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """A L{Window} with standard setup.
 */
struct PyElementaryStandardWindow {
  struct PyElementaryWindow __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_innerwindow.pxi":19
 * #
 * 
 * cdef public class InnerWindow(LayoutClass) [object PyElementaryInnerWindow, type PyElementaryInnerWindow_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """An inwin is a window inside a window that is useful for a quick popup.
 */
struct PyElementaryInnerWindow {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};
struct PyElementaryBackground {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};
struct PyElementaryIcon {
  struct PyElementaryImage __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_box.pxi":52
 * 
 * 
 * cdef public class Box(Object) [object PyElementaryBox, type PyElementaryBox_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """A box arranges objects in a linear fashion, governed by a layout function
 */
struct PyElementaryBox {
  struct PyElementaryObject __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_frame.pxi":19
 * #
 * 
 * cdef public class Frame(LayoutClass) [object PyElementaryFrame, type PyElementaryFrame_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """Frame is a widget that holds some content and has a title.
 */
struct PyElementaryFrame {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};
struct PyElementaryFlip {
  struct PyElementaryObject __pyx_base;
};
struct PyElementaryScroller {
  struct PyElementaryObject __pyx_base;
};
struct PyElementaryLabel {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};
struct PyElementaryTable {
  struct PyElementaryObject __pyx_base;
};
struct PyElementaryClock {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};
struct PyElementaryHover {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_entry.pxi":76
 *     return eahi
 * 
 * cdef public class Entry(Object) [object PyElementaryEntry, type PyElementaryEntry_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """An entry is a convenience widget which shows a box that the user can
 */
struct PyElementaryEntry {
  struct PyElementaryObject __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_bubble.pxi":19
 * #
 * 
 * cdef public class Bubble(LayoutClass) [object PyElementaryBubble, type PyElementaryBubble_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """The Bubble is a widget to show text similar to how speech is
 */
struct PyElementaryBubble {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};
struct PyElementaryPhoto {
  struct PyElementaryObject __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_hoversel.pxi":99
 *             return (_ctouni(cicon_file), _ctouni(cicon_group), cicon_type)
 * 
 * cdef public class Hoversel(Button) [object PyElementaryHoversel, type PyElementaryHoversel_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """A hoversel is a button that pops up a list of items (automatically
 */
struct PyElementaryHoversel {
  struct PyElementaryButton __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_toolbar.pxi":594
 *             #return elm_toolbar_item_state_prev(self.item)
 * 
 * cdef public class Toolbar(Object) [object PyElementaryToolbar, type PyElementaryToolbar_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """A toolbar is a widget that displays a list of items inside a box. It
 */
struct PyElementaryToolbar {
  struct PyElementaryObject __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_list.pxi":330
 *             return _object_item_to_python(elm_list_item_next(self.item))
 * 
 * cdef public class List(Object) [object PyElementaryList, type PyElementaryList_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """A list widget is a container whose children are displayed vertically or
 */
struct PyElementaryList {
  struct PyElementaryObject __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_slider.pxi":19
 * #
 * 
 * cdef public class Slider(LayoutClass) [object PyElementarySlider, type PyElementarySlider_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """The slider adds a draggable "slider" widget for selecting the value of
 */
struct PyElementarySlider {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_naviframe.pxi":130
 *             elm_naviframe_item_title_visible_set(self.item, visible)
 * 
 * cdef public class Naviframe(LayoutClass) [object PyElementaryNaviframe, type PyElementaryNaviframe_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """Naviframe stands for navigation frame. It's a views manager
 */
struct PyElementaryNaviframe {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_radio.pxi":19
 * #
 * 
 * cdef public class Radio(LayoutClass) [object PyElementaryRadio, type PyElementaryRadio_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """Radio is a widget that allows for one or more options to be displayed
 */
struct PyElementaryRadio {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};
struct PyElementaryCheck {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_genlist.pxi":543
 *         return elm_genlist_item_select_mode_get(self.item)
 * 
 * cdef public class Genlist(Object) [object PyElementaryGenlist, type PyElementaryGenlist_Type]:             # <<<<<<<<<<<<<<
 *     """Creates a generic, scalable and extensible list widget.
 * 
 */
struct PyElementaryGenlist {
  struct PyElementaryObject __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_gengrid.pxi":548
 *             self.select_mode_set(value)
 * 
 * cdef public class Gengrid(Object) [object PyElementaryGengrid, type PyElementaryGengrid_Type]:             # <<<<<<<<<<<<<<
 *     """Creates a generic, scalable and extensible grid widget.
 * 
 */
struct PyElementaryGengrid {
  struct PyElementaryObject __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_spinner.pxi":19
 * #
 * 
 * cdef public class Spinner(LayoutClass) [object PyElementarySpinner, type PyElementarySpinner_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """A spinner is a widget which allows the user to increase or decrease
 */
struct PyElementarySpinner {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_notify.pxi":18
 * # along with python-elementary. If not, see <http://www.gnu.org/licenses/>.
 * 
 * cdef public class Notify(Object) [object PyElementaryNotify, type PyElementaryNotify_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """Display a container in a particular region of the parent.
 */
struct PyElementaryNotify {
  struct PyElementaryObject __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_fileselector.pxi":19
 * #
 * 
 * cdef public class Fileselector(LayoutClass) [object PyElementaryFileselector, type PyElementaryFileselector_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """
 */
struct PyElementaryFileselector {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
  PyObject *_cbs;
};
struct PyElementaryFileselectorEntry {
  struct PyElementaryObject __pyx_base;
  PyObject *_cbs;
};
struct PyElementaryFileselectorButton {
  struct PyElementaryButton __pyx_base;
  PyObject *_cbs;
};
struct PyElementarySeparator {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};
struct PyElementaryProgressbar {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_menu.pxi":249
 *         return True
 * 
 * cdef public class Menu(Object) [object PyElementaryMenu, type PyElementaryMenu_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """A menu is a list of items displayed above its parent.
 */
struct PyElementaryMenu {
  struct PyElementaryObject __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_panel.pxi":20
 * #
 * 
 * cdef public class Panel(Object) [object PyElementaryPanel, type PyElementaryPanel_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """A panel is a type of animated container that contains subobjects.
 */
struct PyElementaryPanel {
  struct PyElementaryObject __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_web.pxi":92
 *         traceback.print_exc()
 * 
 * cdef public class Web(Object) [object PyElementaryWeb, type PyElementaryWeb_Type]:             # <<<<<<<<<<<<<<
 *     cdef object _console_message_hook
 * 
 */
struct PyElementaryWeb {
  struct PyElementaryObject __pyx_base;
  PyObject *_console_message_hook;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_actionslider.pxi":19
 * #
 * 
 * cdef public class Actionslider(LayoutClass) [object PyElementaryActionslider, type PyElementaryActionslider_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """An actionslider is a switcher for two or three labels with
 */
struct PyElementaryActionslider {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_calendar.pxi":50
 *         elm_calendar_mark_del(self.obj)
 * 
 * cdef public class Calendar(LayoutClass) [object PyElementaryCalendar, type PyElementaryCalendar_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """This is a calendar widget.
 */
struct PyElementaryCalendar {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_colorselector.pxi":53
 *             elm_colorselector_palette_item_color_set(self.item, r, g, b, a)
 * 
 * cdef public class Colorselector(LayoutClass) [object PyElementaryColorselector, type PyElementaryColorselector_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """A Colorselector is a color selection widget.
 */
struct PyElementaryColorselector {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_index.pxi":121
 *         return item.item
 * 
 * cdef public class Index(LayoutClass) [object PyElementaryIndex, type PyElementaryIndex_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """An index widget gives you an index for fast access to whichever
 */
struct PyElementaryIndex {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_ctxpopup.pxi":41
 *             Py_DECREF(self)
 * 
 * cdef public class Ctxpopup(Object) [object PyElementaryCtxpopup, type PyElementaryCtxpopup_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """Context popup widget.
 */
struct PyElementaryCtxpopup {
  struct PyElementaryObject __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_grid.pxi":19
 * #
 * 
 * cdef public class Grid(Object) [object PyElementaryGrid, type PyElementaryGrid_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """A grid layout widget.
 */
struct PyElementaryGrid {
  struct PyElementaryObject __pyx_base;
};
struct PyElementaryVideo {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_video.pxi":332
 * _install_metaclass(&PyElementaryVideo_Type, ElementaryObjectMeta)
 * 
 * cdef public class Player(LayoutClass) [object PyElementaryPlayer, type PyElementaryPlayer_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """Player is a video player that need to be linked with a L{Video}.
 */
struct PyElementaryPlayer {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_conformant.pxi":19
 * #
 * 
 * cdef public class Conformant(LayoutClass) [object PyElementaryConformant, type PyElementaryConformant_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """The aim is to provide a widget that can be used in elementary apps to
 */
struct PyElementaryConformant {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};
struct PyElementaryDayselector {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};
struct PyElementaryPanes {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};
struct PyElementaryThumb {
  struct PyElementaryObject __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_diskselector.pxi":110
 *             return _object_item_to_python(it)
 * 
 * cdef public class Diskselector(Object) [object PyElementaryDiskselector, type PyElementaryDiskselector_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """A diskselector is a kind of list widget. It scrolls horizontally,
 */
struct PyElementaryDiskselector {
  struct PyElementaryObject __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_datetime.pxi":21
 * from datetime import datetime
 * 
 * cdef public class Datetime(Object) [object PyElementaryDatetime, type PyElementaryDatetime_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """Datetime widget is used to display and input date & time values.
 */
struct PyElementaryDatetime {
  struct PyElementaryObject __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_map.pxi":420
 * 
 * 
 * cdef public class Map(Object)[object PyElementaryMap, type PyElementaryMap_Type]:             # <<<<<<<<<<<<<<
 * 
 *     def __init__(self, evasObject parent):
 */
struct PyElementaryMap {
  struct PyElementaryObject __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_mapbuf.pxi":19
 * #
 * 
 * cdef public class Mapbuf(Object) [object PyElementaryMapbuf, type PyElementaryMapbuf_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """This holds one content object and uses an Evas Map of transformation
 */
struct PyElementaryMapbuf {
  struct PyElementaryObject __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_multibuttonentry.pxi":113
 * 
 * 
 * cdef public class MultiButtonEntry(Object) [object PyElementaryMultiButtonEntry, type PyElementaryMultiButtonEntry_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """A Multibuttonentry is a widget to allow a user enter text and manage
 */
struct PyElementaryMultiButtonEntry {
  struct PyElementaryObject __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_slideshow.pxi":237
 * 
 * 
 * cdef public class Slideshow(LayoutClass) [object PyElementarySlideshow, type PyElementarySlideshow_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """This widget, as the name indicates, is a pre-made image
 */
struct PyElementarySlideshow {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_segment_control.pxi":103
 *             elm_segment_control_item_selected_set(self.item, select)
 * 
 * cdef public class SegmentControl(LayoutClass) [object PyElementarySegmentControl, type PyElementarySegmentControl_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """Segment control widget is a horizontal control made of multiple
 */
struct PyElementarySegmentControl {
  struct __pyx_obj_10elementary_12c_elementary_LayoutClass __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_popup.pxi":68
 *                 self.params[1])
 * 
 * cdef public class Popup(Object) [object PyElementaryPopup, type PyElementaryPopup_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """This widget is an enhancement of L{Notify}.
 */
struct PyElementaryPopup {
  struct PyElementaryObject __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_plug.pxi":21
 * from evas.c_evas cimport Image as evasImage
 * 
 * cdef public class Plug(Object) [object PyElementaryPlug, type PyElementaryPlug_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """An object that allows one to show an image which other process created.
 */
struct PyElementaryPlug {
  struct PyElementaryObject __pyx_base;
};
struct PyElementaryPhotocam {
  struct PyElementaryObject __pyx_base;
};

/* "/home/gustavo/Development/svn/e-svn/trunk/BINDINGS/python/python-elementary/elementary/elementary.c_elementary_flipselector.pxi":66
 *             return _object_item_to_python(elm_flipselector_item_next_get(self.item))
 * 
 * cdef public class FlipSelector(Object) [object PyElementaryFlipSelector, type PyElementaryFlipSelector_Type]:             # <<<<<<<<<<<<<<
 * 
 *     """A flip selector is a widget to show a set of B{text} items, one
 */
struct PyElementaryFlipSelector {
  struct PyElementaryObject __pyx_base;
};

#ifndef __PYX_HAVE_API__elementary__c_elementary

#ifndef __PYX_EXTERN_C
  #ifdef __cplusplus
    #define __PYX_EXTERN_C extern "C"
  #else
    #define __PYX_EXTERN_C extern
  #endif
#endif

__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryObject_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryGestureLayer_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryLayout_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryImage_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryButton_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryWindow_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryStandardWindow_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryInnerWindow_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryBackground_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryIcon_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryBox_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryFrame_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryFlip_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryScroller_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryLabel_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryTable_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryClock_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryHover_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryEntry_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryBubble_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryPhoto_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryHoversel_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryToolbar_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryList_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementarySlider_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryNaviframe_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryRadio_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryCheck_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryGenlist_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryGengrid_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementarySpinner_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryNotify_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryFileselector_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryFileselectorEntry_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryFileselectorButton_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementarySeparator_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryProgressbar_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryMenu_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryPanel_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryWeb_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryActionslider_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryCalendar_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryColorselector_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryIndex_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryCtxpopup_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryGrid_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryVideo_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryPlayer_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryConformant_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryDayselector_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryPanes_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryThumb_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryDiskselector_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryDatetime_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryMap_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryMapbuf_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryMultiButtonEntry_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementarySlideshow_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementarySegmentControl_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryPopup_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryPlug_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryPhotocam_Type;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) PyElementaryFlipSelector_Type;

#endif /* !__PYX_HAVE_API__elementary__c_elementary */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC initc_elementary(void);
#else
PyMODINIT_FUNC PyInit_c_elementary(void);
#endif

#endif /* !__PYX_HAVE__elementary__c_elementary */
