#ifndef __searchfield_h__
#define __searchfield_h__


#include "slew.h"

#include "constants/window.h"
#include "constants/textfield.h"
#include "constants/searchfield.h"

#include <QMenu>
#include <QToolButton>


class SearchField_Impl : public FormattedLineEdit, public WidgetInterface
{
	Q_OBJECT
	
public:
	SL_DECLARE_OBJECT(SearchField)
	
	SL_DECLARE_SET_VISIBLE(FormattedLineEdit)
	
	virtual void setDataType(int dataType) { FormattedLineEdit::setDataType(dataType); }
	virtual int dataType() { return FormattedLineEdit::dataType(); }
	
	virtual bool isModifyEvent(QEvent *event);
	virtual bool canModify() { return WidgetInterface::canModify(this); }
	
	virtual bool isFocusOutEvent(QEvent *event);
	virtual bool canFocusOut(QWidget *oldFocus, QWidget *newFocus);
	
	virtual QAbstractButton *createIconButton(const QIcon& icon);
	
	void setEmptyText(const QString& text) { fEmptyText = text; update(); }
	QString emptyText() { return fEmptyText; }
	
	void setMenu(QMenu *menu);
	QMenu *menu() { return fMenu; }
	
	void setCancellable(bool enabled);
	bool isCancellable() { return fCancelIcon != NULL; }
	
	void updateGeometries();
	virtual QSize sizeHint() const;
	virtual QSize minimumSizeHint() const;
	
	virtual void resizeEvent(QResizeEvent *event);
	virtual void paintEvent(QPaintEvent *event);
	
public slots:
	void handleTextModified(const QString& text, int completion);
	void handleReturnPressed();
	void handleSearchClicked();
	void handleCancelClicked();
	void handleContextMenu();
	
protected:
	QToolButton		*fCancelIcon;
	QString			fEmptyText;
	QMenu			*fMenu;
};


#endif
