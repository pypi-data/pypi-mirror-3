#include "slew.h"

#include "frame.h"
#include "dialog.h"
#include "menubar.h"
#include "statusbar.h"
#include "toolbar.h"
#include "sizer.h"


Frame_Impl::Frame_Impl()
	: QMainWindow(), WidgetInterface(), fResizeable(true), fStatusBar(NULL)
{
	setCentralWidget(new QWidget);
	centralWidget()->setSizePolicy(QSizePolicy::MinimumExpanding, QSizePolicy::MinimumExpanding);
	setAttribute(Qt::WA_QuitOnClose);
// 	setUnifiedTitleAndToolBarOnMac(true);
// 	setAnimated(false);
}


#ifdef Q_WS_WIN

#include "windows.h"

bool
Frame_Impl::winEvent(MSG *msg, long *result)
{
	if ((!fResizeable) && (msg->message == WM_SIZING)) {
		GetWindowRect(msg->hwnd, (LPRECT)msg->lParam);
		*result = TRUE;
		return true;
	}
	return false;
}

#endif


void
Frame_Impl::setResizeable(bool resizeable)
{
	fResizeable = resizeable;
	
#ifdef Q_WS_MAC
	helper_set_resizeable(this, resizeable);
#endif
}


bool
Frame_Impl::event(QEvent *event)
{
#ifdef Q_WS_MAC
	if (event->type() == QEvent::StatusTip) {
		static bool inStatusTip = false;
		bool result;
		
		if (inStatusTip) {
			event->accept();
			return true;
		}
		inStatusTip = true;
		result = QMainWindow::event(event);
		inStatusTip = false;
		return result;
	}
#endif
	
	return QMainWindow::event(event);
}


void
Frame_Impl::moveEvent(QMoveEvent *event)
{
	hidePopupMessage();
}


void
Frame_Impl::resizeEvent(QResizeEvent *event)
{
	hidePopupMessage();
	
	if (event->size() != event->oldSize()) {
		EventRunner runner(this, "onResize");
		if (runner.isValid()) {
			runner.set("size", event->size());
			runner.run();
		}
	}
}


void
Frame_Impl::closeEvent(QCloseEvent *event)
{
	EventRunner runner(this, "onClose");
	if (runner.isValid()) {
		runner.set("accepted", true);
		event->setAccepted(runner.run());
	}
}


SL_DEFINE_METHOD(Frame, insert, {
	int index;
	PyObject *object;
	
	if (!PyArg_ParseTuple(args, "iO", &index, &object))
		return NULL;
	
	QObject *widget = getImpl(object);
	if (!widget)
		SL_RETURN_NO_IMPL;
	
	if (isMenuBar(object)) {
		MenuBar_Impl *child = (MenuBar_Impl *)widget;
		impl->setMenuBar(child);
	}
	else if (isStatusBar(object)) {
		StatusBar_Impl *child = (StatusBar_Impl *)widget;
		child->setSizeGripEnabled(impl->minimumSize() != impl->maximumSize());
		impl->setStatusBar(child);
		impl->setProperty("has_statusbar", true);
	}
	else if (isToolBar(object)) {
		ToolBar_Impl *child = (ToolBar_Impl *)widget;
		impl->addToolBar(child->area(), child);
		child->setVisible(true);
	}
	else {
		return insertWindowChild(impl->centralWidget(), object);
	}
})


SL_DEFINE_METHOD(Frame, remove, {
	PyObject *object;
	
	if (!PyArg_ParseTuple(args, "O", &object))
		return NULL;
	
	QObject *widget = getImpl(object);
	if (!widget)
		SL_RETURN_NO_IMPL;
	
	if (isMenuBar(object)) {
		MenuBar_Impl *child = (MenuBar_Impl *)widget;
		MenuBar_Proxy *proxy = (MenuBar_Proxy *)getProxy(object);
		QList<QAction *> actions = child->actions();
		
		SL_QAPP()->replaceProxyObject((Abstract_Proxy *)proxy, new MenuBar_Impl());
		
		while (!actions.isEmpty()) {
			QAction *action = actions.takeAt(0);
			child->removeAction(action);
			proxy->fImpl->addAction(action);
		}
		impl->setMenuBar(NULL);
	}
	else if (isStatusBar(object)) {
		StatusBar_Impl *child = (StatusBar_Impl *)widget;
		StatusBar_Proxy *proxy = (StatusBar_Proxy *)getProxy(object);
		QList<int> props = child->getProps();
		
		SL_QAPP()->replaceProxyObject((Abstract_Proxy *)proxy, child->clone());
		
		impl->setStatusBar(NULL);
		impl->setProperty("has_statusbar", false);
	}
	else if (isToolBar(object)) {
		ToolBar_Impl *child = (ToolBar_Impl *)widget;
		impl->removeToolBar(child);
	}
	else {
		return removeWindowChild(impl->centralWidget(), object);
	}
})


SL_DEFINE_METHOD(Frame, set_focus, {
	bool focus;
	
	if (!PyArg_ParseTuple(args, "O&", convertBool, &focus))
		return NULL;
	
	if (focus) {
		impl->activateWindow();
		impl->raise();
	}
})


SL_DEFINE_METHOD(Frame, alert, {
	int timeout;
	
	if (!PyArg_ParseTuple(args, "i", &timeout))
		return NULL;
	
	QApplication::alert(impl, timeout);
})


SL_DEFINE_METHOD(Frame, close, {
	impl->close();
})


SL_DEFINE_ABSTRACT_METHOD(Frame, QWidget, center, {
	centerWindow(impl);
})


SL_DEFINE_ABSTRACT_METHOD(Frame, QWidget, maximize, {
	impl->showMaximized();
})


SL_DEFINE_ABSTRACT_METHOD(Frame, QWidget, is_maximized, {
	return createBoolObject(impl->isMaximized());
})


SL_DEFINE_ABSTRACT_METHOD(Frame, QWidget, minimize, {
	impl->showMinimized();
})


SL_DEFINE_ABSTRACT_METHOD(Frame, QWidget, is_minimized, {
	return createBoolObject(impl->isMinimized());
})


SL_DEFINE_ABSTRACT_METHOD(Frame, QWidget, is_active, {
	return createBoolObject(impl->isActiveWindow());
})


SL_DEFINE_ABSTRACT_METHOD(Frame, QWidget, save_geometry, {
	return createBufferObject(impl->saveGeometry());
})


SL_DEFINE_ABSTRACT_METHOD(Frame, QWidget, restore_geometry, {
	QByteArray state;
	
	if (!PyArg_ParseTuple(args, "O&", convertBuffer, &state))
		return NULL;
	
	impl->restoreGeometry(state);
})


SL_DEFINE_METHOD(Frame, get_style, {
	int style = 0;
	Qt::WindowFlags flags = impl->windowFlags();
	Qt::WindowStates state = impl->windowState();
	
	if ((flags & Qt::WindowType_Mask) == Qt::Tool)
		style |= SL_FRAME_STYLE_MINI;
	if (flags & Qt::WindowTitleHint)
		style |= SL_FRAME_STYLE_CAPTION;
	if (flags & Qt::WindowMinimizeButtonHint)
		style |= SL_FRAME_STYLE_MINIMIZE_BOX;
	if (flags & Qt::WindowMaximizeButtonHint)
		style |= SL_FRAME_STYLE_MAXIMIZE_BOX;
	if (flags & Qt::WindowCloseButtonHint)
		style |= SL_FRAME_STYLE_CLOSE_BOX;
	if (flags & Qt::WindowStaysOnTopHint)
		style |= SL_FRAME_STYLE_STAY_ON_TOP;
	if (impl->isResizeable())
		style |= SL_FRAME_STYLE_RESIZEABLE;
	if (impl->isWindowModified())
		style |= SL_FRAME_STYLE_MODIFIED;
	if (state & Qt::WindowMinimized)
		style |= SL_FRAME_STYLE_MINIMIZED;
	else if (state & Qt::WindowMaximized)
		style |= SL_FRAME_STYLE_MAXIMIZED;
	if (impl->testAttribute(Qt::WA_TranslucentBackground))
		style |= SL_WINDOW_STYLE_TRANSLUCENT;
	if (impl->windowModality() == Qt::ApplicationModal)
		style |= SL_FRAME_STYLE_MODAL;
	
	return PyInt_FromLong(style);
})


SL_DEFINE_METHOD(Frame, set_style, {
	int style;
	
	if (!PyArg_ParseTuple(args, "i", &style))
		return NULL;
	
	Qt::WindowFlags flags = (impl->windowFlags() & Qt::WindowType_Mask) | Qt::CustomizeWindowHint;
	Qt::WindowStates state = impl->windowState();
	
	if (style & SL_FRAME_STYLE_MINI)
		flags = (flags & ~Qt::WindowType_Mask) | Qt::Tool;
	if (style & SL_FRAME_STYLE_CAPTION)
		flags |= Qt::WindowTitleHint;
	if (style & SL_FRAME_STYLE_MINIMIZE_BOX)
		flags |= Qt::WindowMinimizeButtonHint | Qt::WindowSystemMenuHint;
	if (style & SL_FRAME_STYLE_MAXIMIZE_BOX)
		flags |= Qt::WindowMaximizeButtonHint | Qt::WindowSystemMenuHint;
	if (style & SL_FRAME_STYLE_CLOSE_BOX)
		flags |= Qt::WindowCloseButtonHint | Qt::WindowSystemMenuHint;
	if (style & SL_FRAME_STYLE_STAY_ON_TOP)
		flags |= Qt::WindowStaysOnTopHint;
	if ((style & SL_WINDOW_STYLE_FRAMELESS) || (!(flags & (Qt::WindowMinimizeButtonHint | Qt::WindowMaximizeButtonHint | Qt::WindowCloseButtonHint))))
		flags |= Qt::FramelessWindowHint;
	
	flags |= Qt::Window;
	bool visible = impl->isVisible();
	if ((flags ^ impl->windowFlags()) & ~Qt::MacWindowToolBarButtonHint) {
		impl->setWindowFlags(flags);
	}
	impl->setWindowModality(style & SL_FRAME_STYLE_MODAL ? Qt::ApplicationModal : Qt::NonModal);
	
	impl->setResizeable(style & SL_FRAME_STYLE_RESIZEABLE ? true : false);
	
	if (qvariant_cast<bool>(impl->property("has_statusbar"))) {
		impl->statusBar()->setSizeGripEnabled(style & SL_FRAME_STYLE_RESIZEABLE ? true : false);
	}
	
	if ((style & SL_FRAME_STYLE_MAXIMIZED) && (!(state & Qt::WindowMaximized)))
		impl->setWindowState((state & ~Qt::WindowMinimized) | Qt::WindowMaximized);
	else if ((style & SL_FRAME_STYLE_MINIMIZED) && (!(state & Qt::WindowMinimized)))
		impl->setWindowState((state & ~Qt::WindowMaximized) | Qt::WindowMinimized);
	else if (((style & (SL_FRAME_STYLE_MINIMIZED | SL_FRAME_STYLE_MAXIMIZED)) == 0) && (state & (Qt::WindowMaximized | Qt::WindowMinimized)))
		impl->setWindowState(state & ~(Qt::WindowMinimized | Qt::WindowMaximized));
	
	impl->setWindowModified(style & SL_FRAME_STYLE_MODIFIED ? true : false);
	impl->setAttribute(Qt::WA_TranslucentBackground, style & SL_WINDOW_STYLE_TRANSLUCENT ? true : false);
	if (visible)
		impl->setVisible(visible);
})


SL_DEFINE_ABSTRACT_METHOD(Frame, QWidget, get_title, {
	return createStringObject(impl->windowTitle());
})


SL_DEFINE_ABSTRACT_METHOD(Frame, QWidget, set_title, {
	QString title;
	
	if (!PyArg_ParseTuple(args, "O&", convertString, &title))
		return NULL;
	
	impl->setWindowTitle(title);
})


SL_START_PROXY_DERIVED(Frame, Window)
SL_METHOD(insert)
SL_METHOD(remove)
SL_METHOD(set_focus)
SL_METHOD(alert)

SL_METHOD(close)
SL_METHOD(center)
SL_METHOD(maximize)
SL_METHOD(is_maximized)
SL_METHOD(minimize)
SL_METHOD(is_minimized)
SL_METHOD(is_active)
SL_METHOD(save_geometry)
SL_METHOD(restore_geometry)

SL_PROPERTY(style)
SL_PROPERTY(title)
SL_END_PROXY_DERIVED(Frame, Window)


#include "frame.moc"
#include "frame_h.moc"

