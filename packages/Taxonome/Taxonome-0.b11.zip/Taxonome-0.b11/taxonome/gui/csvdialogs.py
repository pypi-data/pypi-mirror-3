"""GUI Dialogs for loading CSV files.
"""
import os.path
import csv
from .qt import QtGui, QtCore

from . import iothread

def _preview_csv(preview, filename, encoding='utf-8'):
    """Open file, grab column names, and preview the first 10 rows.
    
    preview should be a QTableWidget to put the preview in.
    """
    # Fill in preview table from CSV file
    with open(filename, encoding=encoding, errors='replace') as f:
        csvin = csv.reader(f)
        fields = next(csvin)
        head = [next(csvin) for _ in range(10)]
    
    for i in range(len(fields)):
        preview.insertColumn(i)
    preview.setHorizontalHeaderLabels(fields)
    for i, row in enumerate(head):
        preview.insertRow(i)
        for j, cell in enumerate(row):
            preview.setItem(i, j, QtGui.QTableWidgetItem(cell))
    
    return fields

def prepare_csv(optsdialog, filename, encoding='utf-8'):
    fields = _preview_csv(optsdialog.preview, filename, encoding)
    # Prepare CSV field dropdowns
    optsdialog.namefield.addItems(fields)
    optsdialog.authfield.addItems(fields)
    optsdialog.authfield.setCurrentIndex(1)

supported_encodings = ["UTF-8", "Windows-1252", "IBM850"]

def _get_auth_field(csvdialog, prefix=''):
    if getattr(csvdialog, prefix+'noauth').isChecked():
        return None
    elif getattr(csvdialog, prefix+'auth_with_name').isChecked():
        return True
    else:
        return getattr(csvdialog, prefix+'authfield').currentText()

def load_csv(app):
    """Load a user-selected CSV file into the application."""
    filename = QtGui.QFileDialog.getOpenFileName(app, "Open file",
                            app.lastdir, "CSV (*.csv);;All files (*.*)")
    if not filename:
        return
    app.lastdir = os.path.dirname(filename)
    
    from .ui.csvimport import Ui_CsvImportDialog
    dialog = QtGui.QDialog()
    csvdialog = Ui_CsvImportDialog()
    csvdialog.setupUi(dialog)
    
    prepare_csv(csvdialog, filename)
    
    def redecode_csv(encoding):
        "Switch encoding for reading CSV file."
        csvdialog.namefield.clear()
        csvdialog.authfield.clear()
        prepare_csv(csvdialog, filename, encoding)
    QtCore.QObject.connect(csvdialog.csv_encoding,
            QtCore.SIGNAL("currentIndexChanged(QString)"), redecode_csv)
    
    csvdialog.csv_encoding.addItems(supported_encodings)
    
    ds_name = os.path.splitext(os.path.basename(filename))[0].replace("_"," ")
    csvdialog.ds_name.setText(ds_name)
    
    if not dialog.exec_():
        return

    namefield = csvdialog.namefield.currentText()
    authfield = _get_auth_field(csvdialog)
    encoding = csvdialog.csv_encoding.currentText()
    
    iothread.load_csv(app, csvdialog.ds_name.text(), filename, encoding=encoding,
                                namefield=namefield, authfield=authfield)


def load_csv_synonyms(app):
    """Load a user-selected CSV file of synonyms into the application."""
    filename = QtGui.QFileDialog.getOpenFileName(app, "Open file",
                            app.lastdir, "CSV (*.csv);;All files (*.*)")
    if not filename:
        return
    app.lastdir = os.path.dirname(filename)
    
    from .ui.csvimport_synonyms import Ui_CsvSynonymsImportDialog
    dialog = QtGui.QDialog()
    csvdialog = Ui_CsvSynonymsImportDialog()
    csvdialog.setupUi(dialog)
    
    fields = _preview_csv(csvdialog.preview, filename)
    
    csvdialog.accnamefield.addItems(fields)
    csvdialog.accauthfield.addItems(fields)
    csvdialog.accauthfield.setCurrentIndex(1)
    csvdialog.synnamefield.addItems(fields)
    csvdialog.synnamefield.setCurrentIndex(2)
    csvdialog.synauthfield.addItems(fields)
    csvdialog.synauthfield.setCurrentIndex(3)
    
    ds_name = os.path.splitext(os.path.basename(filename))[0].replace("_"," ")
    csvdialog.ds_name.setText(ds_name)
    
    if not dialog.exec_():
        return

    accnamefield = csvdialog.accnamefield.currentText()
    synnamefield = csvdialog.synnamefield.currentText()
    accauthfield = _get_auth_field(csvdialog, 'acc')
    synauthfield = _get_auth_field(csvdialog, 'syn')
    
    iothread.load_csv_synonyms(app, csvdialog.ds_name.text(), filename, accnamefield=accnamefield,
                accauthfield=accauthfield, synnamefield=synnamefield, synauthfield=synauthfield)

def load_csv_individuals(app):
    """Load a user-selected CSV file of individual records into the application."""
    filename = QtGui.QFileDialog.getOpenFileName(app, "Open file",
                            app.lastdir, "CSV (*.csv);;All files (*.*)")
    if not filename:
        return
    app.lastdir = os.path.dirname(filename)
    
    from .ui.csvimport import Ui_CsvImportDialog
    dialog = QtGui.QDialog()
    csvdialog = Ui_CsvImportDialog()
    csvdialog.setupUi(dialog)
    
    prepare_csv(csvdialog, filename)
    
    def redecode_csv(encoding):
        "Switch encoding for reading CSV file."
        csvdialog.namefield.clear()
        csvdialog.authfield.clear()
        prepare_csv(csvdialog, filename, encoding)
    QtCore.QObject.connect(csvdialog.csv_encoding,
            QtCore.SIGNAL("currentIndexChanged(QString)"), redecode_csv)
    
    csvdialog.csv_encoding.addItems(supported_encodings)
    
    ds_name = os.path.splitext(os.path.basename(filename))[0].replace("_"," ")
    csvdialog.ds_name.setText(ds_name)
    
    if not dialog.exec_():
        return

    namefield = csvdialog.namefield.currentText()
    authfield = _get_auth_field(csvdialog)
    encoding = csvdialog.csv_encoding.currentText()
    
    iothread.load_csv_individuals(app, csvdialog.ds_name.text(), filename, encoding=encoding,
                                namefield=namefield, authfield=authfield)
