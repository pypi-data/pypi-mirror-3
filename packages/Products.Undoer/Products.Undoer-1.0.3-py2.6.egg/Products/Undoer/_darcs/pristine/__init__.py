from Globals import MessageDialog, DTMLFile, InitializeClass
from DateTime import DateTime
import types
from App.Undo import UndoSupport

def undo_changes_by_date(self, date=None, REQUEST=None):
    """Undoes changes made to the database after a given date;  if
    a date is not specified, all changes are undone."""
    if date is None:
        date = float(0)
    elif type(date) == types.StringType:
        date = float(DateTime(date))
    else:
        date = float(date)
    transactions = self._p_jar.db().undoLog(0, 2**32)
    db = self._p_jar.db()
    count = 0
    undoable_transactions = []
    for transaction in transactions:
        if transaction['time'] >= date:
            undoable_transactions.append(transaction['id'])
            count += 1
    if hasattr(db, 'undoMultiple'):
        db.undoMultiple(undoable_transactions)
    else:
        for transaction_id in undoable_transactions:
            db.undo(transaction_id)
    if REQUEST:
        return MessageDialog(
		title='Result of undoing transactions',
		message="<em>%s</em> transactions were undone" % count,
		action='./manage_UndoForm'
	)
    return count

UndoSupport.undo_changes_by_date = undo_changes_by_date
UndoSupport.manage_UndoForm = DTMLFile(
	'dtml/undo',
	globals(),
	PrincipiaUndoBatchSize=20,
	first_transaction=0,
	last_transaction=20
)
UndoSupport.__ac_permissions__ = (
	('Undo changes', (
		'manage_undo_transactions',
		'undoable_transactions',
		'manage_UndoForm',
		'undo_changes_by_date',
	)),
)
InitializeClass(UndoSupport)
