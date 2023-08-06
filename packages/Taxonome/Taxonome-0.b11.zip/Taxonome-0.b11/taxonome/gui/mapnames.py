"""GUI Dialogs for mapping one set of names to another.
"""
import csv
import os.path
from functools import partial

from .qt import QtGui, QtCore

from taxonome.taxa import match_taxa
from taxonome.taxa import file_csv
from taxonome.taxa.collection import run_match_taxa
from taxonome import tracker
from .ui.map_names_wizard import Ui_MapNamesWizard
from .csvdialogs import prepare_csv, _get_auth_field, supported_encodings
from .iothread import Worker, makeloader

def getoptions(app, optsdialog):
    """Find what options the user selected from the dialog for matching taxa."""
    
    if optsdialog.upgrade_all.isChecked():
        upgrade = 'all'
    elif optsdialog.upgrade_none.isChecked():
        upgrade = 'none'
    else:
        upgrade = 'nominal'
    
    if optsdialog.preferaccepted_all.isChecked():
        prefer_accepted = 'all'
    elif optsdialog.preferaccepted_none.isChecked():
        prefer_accepted = 'none'
    else:
        prefer_accepted = 'noauth'
    strict_authority = not optsdialog.auth_lax.isChecked()
    user_choice = optsdialog.user_choice.isChecked()
    
    return upgrade, prefer_accepted, strict_authority, user_choice

def _select_save_location(app, parent, destination):
    """Make a function to get an output filename and put it in a text box."""
    def inner():
        filename = QtGui.QFileDialog.getSaveFileName(parent, "Save file to:",
                            app.lastdir, "CSV (*.csv);;All files (*.*)")
        if filename:
            if not os.path.splitext(filename)[1]:
                filename += '.csv'
            destination.setText(filename)
    return inner

def wizard_map_names(app):
    """Match a big dataset (a CSV file, can be too big to hold in memory) against
    one of the loaded datasets.
    
    Presents the user with a set of options for controlling input, matching and
    output.
    """
    optswizard = Ui_MapNamesWizard()
    optswizard.wizard = QtGui.QWizard()
    optswizard.setupUi(optswizard.wizard)
    optswizard.taxa_dataset.setModel(app.datasets_model)
    optswizard.target_dataset.setModel(app.datasets_model)
    optswizard.csv_encoding.addItems(supported_encodings)
    
    def select_csv_in():
        filename = QtGui.QFileDialog.getOpenFileName(optswizard.wizard, "Select big CSV file",
                                    app.lastdir, "CSV (*.csv);;All files (*.*)")
        if not filename:
            return
        optswizard.from_csv_file.setText(filename)
        prepare_csv(optswizard, filename)
    
    def redecode_csv(encoding):
        "Switch encoding for reading CSV file."
        filename = optswizard.from_csv_file.text()
        optswizard.namefield.clear()
        optswizard.authfield.clear()
        prepare_csv(optswizard, filename, encoding)
    
    def select_dataset_next_page():
        # Skip the CSV import page if we're using taxa from a local dataset.
        if optswizard.from_csv.isChecked():
            return 1
        # Skip the matching options if we're using TNRS
        elif optswizard.to_tnrs.isChecked():
            return 3
        return 2
    optswizard.datasets_page.nextId = select_dataset_next_page
    
    def csv_opts_next_page():
        # Skip the matching options if we're using TNRS
        return 3 if optswizard.to_tnrs.isChecked() else 2
    
    # Browse buttons for input & output files
    optswizard.from_csv_browse.clicked.connect(select_csv_in)
    optswizard.taxadata_browse.clicked.connect(_select_save_location(app, optswizard.wizard, optswizard.taxadata_file))
    optswizard.mappings_browse.clicked.connect(_select_save_location(app, optswizard.wizard, optswizard.mappings_file))
    optswizard.log_browse.clicked.connect(_select_save_location(app, optswizard.wizard, optswizard.log_file))
    
    # Encoding switcher for CSV file
    # The signal from QComboBox is overloaded - we want the str form
    QtCore.QObject.connect(optswizard.csv_encoding,
            QtCore.SIGNAL("currentIndexChanged(QString)"), redecode_csv)
    
    # Run the wizard
    if not optswizard.wizard.exec_():
        return False
    
    # Get the options
    seln = optswizard.target_dataset.currentIndex()
    target = app.datasets_model.item(seln)
    if optswizard.from_csv.isChecked():
        csv_filename = optswizard.from_csv_file.text()
        from_csv = True
    else:
        seln = optswizard.taxa_dataset.currentIndex()
        dataset_item = app.datasets_model.item(seln)
        taxa_dataset = dataset_item.ds
        from_csv = False
    
    to_tnrs = optswizard.to_tnrs.isChecked()
    
    upgrade, prefer_accepted, strict_authority, user_choice = getoptions(app, optswizard)
    
    namefield = optswizard.namefield.currentText()
    authfield = _get_auth_field(optswizard)
    csv_encoding = optswizard.csv_encoding.currentText()
    
    nameselector = app.gui_select_name if user_choice else app.silent_select_name

    # Output options
    taxadata_file, mappings_file, log_file = None, None, None
    if optswizard.taxadata.isChecked():
        taxadata_file = optswizard.taxadata_file.text()
    if optswizard.mappings.isChecked():
        mappings_file = optswizard.mappings_file.text()
    if optswizard.log.isChecked():
        log_file = optswizard.log_file.text()
    matched_ds = optswizard.matched_ds.isChecked()
    
    trackers = []
    files = []
    if mappings_file:
        f = open(mappings_file, "w", encoding='utf-8', newline='')
        files.append(f)
        trackers.append(tracker.CSVListMatches(f))
    if log_file:
        f = open(log_file, "w", encoding='utf-8', newline='')
        files.append(f)
        trackers.append(tracker.CSVTracker(f))
    if taxadata_file:
        if from_csv:
            with open(csv_filename, encoding=csv_encoding, errors='replace', newline='') as f:
                fields = next(csv.reader(f))
            fields.remove(namefield)
            if isinstance(authfield, str):
                fields.remove(authfield)
        else:
            fields = set()
            for t in taxa_dataset: fields.update(t.info)
            fields = list(fields)
        f = open(taxadata_file, "w", encoding='utf-8', newline='')
        files.append(f)
        trackers.append(tracker.CSVTaxaTracker(f, fields))
    
    def _run(progress=None):
        "Called in a separate thread to run the matching."
        if from_csv:
            csvfile = open(csv_filename, encoding=csv_encoding, errors='replace')
            files.append(csvfile)
            data_in = file_csv.iter_taxa(csvfile, namefield=namefield, authfield=authfield, tracker=trackers, progress=progress)
        else:
            if progress:
                trackers.append(tracker.Counter(progress))
            data_in = taxa_dataset
        
        if to_tnrs:
            # Match to TNRS
            if from_csv:
                csvfile2 = open(csv_filename, encoding=csv_encoding, errors='replace')
                files.append(csvfile2)
                data_in2 = file_csv.iter_taxa(csvfile2, namefield=namefield, authfield=authfield)
            else:
                data_in2 = None
            
            from taxonome.services import tnrs
            # Do we want the output as a dataset?
            matchfunc = tnrs.match_taxa if matched_ds else tnrs.run_match_taxa
            # Run the matching
            res = matchfunc(data_in, data_in2, tracker=trackers)
        
        else:
            # Match to dataset
            
            # Do we want the output as a dataset?
            matchfunc = match_taxa if matched_ds else run_match_taxa
            # Run the matching
            res = matchfunc(data_in, target.ds, upgrade_subsp=upgrade,
                strict_authority=strict_authority, nameselector=nameselector, tracker=trackers)
        
        for f in files: f.close()
        return res
    
    steps = os.stat(csv_filename).st_size if from_csv else len(taxa_dataset)
    if matched_ds:
        fromname = os.path.basename(csv_filename) if from_csv else dataset_item.name
        ds_name = "{} mapped to {}".format(fromname, target.name)
        makeloader(app, _run, ds_name, steps)
    else:
        thread = Worker(_run, app)
        thread.error_raised.connect(app.show_error)
        thread.withprogress(app, steps)
        thread.start()
