"""
This addon and all code included is open-source under the Apache-2.0 License

CREDIT TO Batch Editing ADDON https://ankiweb.net/shared/info/291119185
Most of the code structure is based on ^this^ addon

Author:         Dillon Wall
Description:    An addon for Anki that downloads and adds audio in a bulk operation to the user-selected cards.
                This addon makes use of URLs to submit API requests and download audio from any URL the user specifies
                    in an order of priority.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import time

from aqt.qt import *
from aqt.utils import tooltip

from anki.hooks import addHook
from aqt import mw
from aqt.operations import QueryOp

from .audiodownloader import *

# Config setup
config = mw.addonManager.getConfig(__name__)


def deleteItemsOfLayout(layout):
    """
    Helper function that recursively deletes all items within a layout
    """
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
            else:
                deleteItemsOfLayout(item.layout())


class SourceHBox(QHBoxLayout):
    def __init__(self, priority, changePriority, removeSource, parentDialog):
        QHBoxLayout.__init__(self)

        self.priority = priority
        self.changePriority = changePriority
        self.removeSource = removeSource
        self.parentDialog = parentDialog

        self.position_label = QLabel(str(self.priority) + ": ")

        self.name_textbox = QLineEdit()
        self.name_textbox.setPlaceholderText("Enter Name")
        self.name_textbox.setMaximumWidth(80)

        self.cu_textbox = QLineEdit()
        self.cu_textbox.setPlaceholderText("Enter Custom URL")

        self.source_button_box = QDialogButtonBox(Qt.Orientation.Horizontal, self.parentDialog)
        self.source_button_box.setMaximumWidth(60)
        self.moveup_btn = self.source_button_box.addButton("^",
                                        QDialogButtonBox.ButtonRole.ActionRole)
        self.moveup_btn.setToolTip("Move this source up in priority")
        self.moveup_btn.clicked.connect(lambda state, dir="up": self.changePriorityHelper(dir))
        self.movedown_btn = self.source_button_box.addButton("v",
                                        QDialogButtonBox.ButtonRole.ActionRole)
        self.movedown_btn.setToolTip("Move this source down in priority")
        self.movedown_btn.clicked.connect(lambda state, dir="down": self.changePriorityHelper(dir))
        self.remove_btn = self.source_button_box.addButton("X",
                                        QDialogButtonBox.ButtonRole.ActionRole)
        self.remove_btn.setToolTip("Remove this source")
        self.remove_btn.clicked.connect(lambda state: self.removeSourceHelper())

        self.addWidget(self.position_label)
        self.addWidget(self.name_textbox)
        self.addWidget(self.cu_textbox)
        self.addWidget(self.source_button_box)

    def changePriorityNumber(self, amount):
        self.priority += amount
        self.setPriorityNumber(self.priority)

    def setPriorityNumber(self, amount):
        self.priority = amount
        self.position_label.setText(str(self.priority) + ": ")
        self.position_label.repaint()

    def changePriorityHelper(self, dir):
        self.changePriority(dir, self.priority)

    def removeSourceHelper(self):
        self.removeSource(self.priority)

    def getInfo(self):
        return self.name_textbox.text(), self.cu_textbox.text()

    def loadFromDict(self, dict):
        self.setPriorityNumber(dict['priority'])
        self.name_textbox.setText(dict['name'])
        self.cu_textbox.setText(dict['url'])

    def saveAsDict(self):
        dict = {
            'priority': self.priority,
            'name': self.name_textbox.text(),
            'url': self.cu_textbox.text()
        }
        return dict


class BulkGenerateDialog(QDialog):
    """Browser batch editing main dialog"""

    def __init__(self, browser, nids):
        QDialog.__init__(self, parent=browser)
        self.browser = browser
        self.nids = nids
        self.num_sources = 0
        self.sources = []
        self.sources_vbox = QVBoxLayout()

        self._setupUi()

    def saveSourcesToConfig(self):
        """
        Saves just the sources to the config
        (I should get rid of this function and put the functionality in saveConfig since we really only need to call
            saveConfig when the window closes)
        """
        sourcesDict = []
        for s in self.sources:
            sourcesDict.append(s.saveAsDict())

        config['sources'] = sourcesDict
        mw.addonManager.writeConfig(__name__, config)

    def saveConfig(self):
        """
        Saves all UI elements to the config
        """
        self.saveSourcesToConfig()
        config['fsel'] = self.fsel.currentText()
        config['delay_sb'] = self.delay_sb.value()
        config['ksel'] = self.ksel.currentText()
        config['dup_cb'] = self.dup_cb.isChecked()
        config['danger_cb'] = self.danger_cb.isChecked()
        mw.addonManager.writeConfig(__name__, config)

    def loadConfig(self):
        """
        Loads all UI elements from the config
        """
        if config['sources'] and len(config['sources']) > 0:
            for i, s in enumerate(config['sources']):
                self.addSource()
                self.sources[i].loadFromDict(s)
        else:
            self.addSource()
            self.saveSourcesToConfig()

        if config['fsel'] and self.fsel.findText(config['fsel']):
            self.fsel.setCurrentText(config['fsel'])
        if config['delay_sb']:
            self.delay_sb.setValue(config['delay_sb'])
        if config['ksel'] and self.ksel.findText(config['ksel']):
            self.ksel.setCurrentText(config['ksel'])
        if config['dup_cb']:
            self.dup_cb.setChecked(config['dup_cb'])
        if config['danger_cb']:
            self.danger_cb.setChecked(config['danger_cb'])

    def closeEvent(self, evnt):
        """
        Overrides the closeEvent of the main window
        Before closing, it saves all UI elements to the config
        """
        self.saveConfig()
        super(BulkGenerateDialog, self).closeEvent(evnt)

    def _setupUi(self):
        """
        Sets up all the UI elements in the main BulkGenerateDialog window
        """
        # Target audio field, Filter kana field, Delay spin box, and Duplicate check box
        flabel = QLabel("Audio field:")
        flabel.setToolTip("This specifies the field that will get REPLACED with the downloaded audio clip on every selected card")
        self.fsel = QComboBox()
        fields = self._getFields()
        self.fsel.addItems(fields)

        dlabel = QLabel("Delay between requests:")
        dlabel.setToolTip("This specifies the delay in seconds between each HTTP request to download audio.\n\nIf you are downloading from Forvo or another source that has bot detection, use a VPN or set this to a higher delay.")
        self.delay_sb = QDoubleSpinBox()
        self.delay_sb.setDecimals(1)
        self.delay_sb.setMinimum(0)
        self.delay_sb.setMaximum(999)
        self.delay_sb.setValue(0)

        klabel = QLabel("Filter kana:")
        klabel.setToolTip("This specifies a field to filter out all characters except hiragana.\n\nThis is useful for the 'Reading' field if you have it in the form 私[わたし] instead of わたし.")
        self.ksel = QComboBox()
        fields = self._getFields()
        self.ksel.addItem("(None)")
        self.ksel.addItems(fields)

        duplabel = QLabel("Duplicate to empty fields:")
        duplabel.setToolTip("If enabled, will duplicate the previously used URL parameter to the next parameter if empty.")
        self.dup_cb = QCheckBox()
        self.dup_cb.setChecked(True)

        dangerlabel = QLabel("Dangerously fast:")
        dangerlabel.setToolTip("If enabled, will run 0.1s faster per card, but likely give you errors.")
        self.danger_cb = QCheckBox()

        f_grid = QGridLayout()
        f_grid.addWidget(flabel, 0, 1)
        f_grid.addWidget(self.fsel, 0, 2)
        f_grid.setColumnStretch(3, 1)
        f_grid.addWidget(duplabel, 0, 4, 1, 3)
        f_grid.addWidget(self.dup_cb, 0, 7)
        f_grid.setColumnStretch(8, 2)

        f_grid.addWidget(klabel, 1, 1)
        f_grid.addWidget(self.ksel, 1, 2)
        f_grid.addWidget(dangerlabel, 1, 4, 1, 3)
        f_grid.addWidget(self.danger_cb, 1, 7)

        f_grid.addWidget(dlabel, 2, 1)
        f_grid.addWidget(self.delay_sb, 2, 2)

        # setup buttons
        button_box_hbox = QHBoxLayout()
        # button box LEFT
        button_box_vbox_left = QVBoxLayout()
        button_box_left = QDialogButtonBox(Qt.Orientation.Horizontal, self)

        addsource_btn = button_box_left.addButton("Add source",
                                        QDialogButtonBox.ButtonRole.ActionRole)
        addsource_btn.setToolTip("Add a new source")
        addsource_btn.clicked.connect(lambda state: self.addSource())

        button_box_vbox_left.addWidget(button_box_left, alignment=Qt.AlignmentFlag.AlignLeft)

        # button box RIGHT
        button_box_vbox_right = QVBoxLayout()
        button_box_right = QDialogButtonBox(Qt.Orientation.Horizontal, self)

        generate_btn = button_box_right.addButton("Generate",
                                        QDialogButtonBox.ButtonRole.ActionRole)
        generate_btn.setToolTip("Generate audio for all selected cards")
        generate_btn.clicked.connect(lambda state: self.onGenerate())
        button_box_vbox_right.addWidget(button_box_right)

        # bottom controls layout
        self.layout_bottom = QVBoxLayout()
        self.layout_bottom.addLayout(f_grid)
        self.layout_bottom.addSpacing(20)
        button_box_hbox.addLayout(button_box_vbox_left)
        button_box_hbox.addLayout(button_box_vbox_right)
        self.layout_bottom.addLayout(button_box_hbox)

        # main vbox layout
        self.vbox_main = QVBoxLayout()
        self.vbox_main.addLayout(self.sources_vbox)
        self.vbox_main.addLayout(self.layout_bottom)

        # alignment
        self.layout_bottom.setAlignment(Qt.AlignmentFlag.AlignBottom)
        button_box_vbox_left.setAlignment(Qt.AlignmentFlag.AlignLeft)
        button_box_vbox_right.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.setLayout(self.vbox_main)
        generate_btn.setFocus()
        self.setMinimumWidth(540)
        self.setMinimumHeight(400)
        self.setWindowTitle("Bulk Generate Audio for Selected Notes")

        self.loadConfig()

    def _changePriority(self, dir, source):
        """
        Changes the priority of a source in the list
        """
        if dir == 'up' and source > 1:
            # modify this one and the above one
            self.sources[source - 1].changePriorityNumber(-1)
            self.sources[source - 2].changePriorityNumber(1)

            temp = self.sources[source - 1]
            self.sources[source - 1] = self.sources[source - 2]
            self.sources[source - 2] = temp

            for source_id in range(source - 1, self.num_sources + 1):
                self.sources_vbox.removeItem(self.sources[source_id - 1])
                self.sources_vbox.insertLayout(source_id - 1, self.sources[source_id - 1])
        elif dir == 'down' and source < self.num_sources:
            # modify this one and the below one
            self.sources[source].changePriorityNumber(-1)
            self.sources[source - 1].changePriorityNumber(1)

            temp = self.sources[source]
            self.sources[source] = self.sources[source - 1]
            self.sources[source - 1] = temp

            for source_id in range(source, self.num_sources + 1):
                self.sources_vbox.removeItem(self.sources[source_id - 1])
                self.sources_vbox.insertLayout(source_id - 1, self.sources[source_id - 1])

    def _removeSource(self, source):
        """
        Removes a source from the list of sources
        """
        self.num_sources -= 1
        deleteItemsOfLayout(self.sources[source - 1])
        self.sources_vbox.removeItem(self.sources[source - 1])
        for source_id in range(source + 1, self.num_sources + 2):
            self.sources[source_id - 1].changePriorityNumber(-1)

        del self.sources[source - 1]

    def _getFields(self):
        """
        Returns all the fields on the first card selected
        Note: That this means if multiple different card types are selected, there may be some issues/unsuccessful cards
        """
        nid = self.nids[0]
        mw = self.browser.mw
        model = mw.col.getNote(nid).model()
        fields = mw.col.models.fieldNames(model)
        return fields

    def addSource(self):
        """
        Adds a new SourceHBox to the list of sources
        """
        self.num_sources += 1
        source = SourceHBox(priority=self.num_sources, changePriority=self._changePriority, removeSource=self._removeSource,
                             parentDialog=self)
        self.sources.append(source)
        self.sources_vbox.addLayout(source)

    def onGenerate(self):
        """
        Actually generate the audio for each card selected
        This is the on call function for the generate button
        """
        filter_kana_fld = self.ksel.currentText()
        duplicate_fld = self.dup_cb.isChecked()
        sleep_time = self.delay_sb.value() + (0.0 if self.danger_cb.isChecked() else 0.1)
        audio_sources = {}
        for source in self.sources:
            name, url = source.getInfo()
            audio_sources.update({name: url})

        browser = self.browser
        mw = browser.mw
        nids = self.nids
        audio_fld = self.fsel.currentText()
        ad = AudioDownloader(audio_sources, mw)

        mw.checkpoint("batch add audio")
        mw.progress.start()
        browser.model.beginReset()

        op = QueryOp(
            parent=mw,
            op=lambda col: _processNotes(browser, nids, audio_fld, sleep_time, filter_kana_fld, ad, duplicate_fld),
            success=_processNotesOnSuccess
        )
        op.with_progress().run_in_background()


def _processNotes(browser, nids, audio_fld, sleep_time, filter_kana_fld, ad, duplicate_fld):
    """
    The main function that handles downloading and adding audio to each card
    This function is meant to run in the background as to not hang the main window
    """
    total = len(nids)
    cnt = 0
    last_progress = 0
    for nid in nids:
        # Update progress
        if time.time() - last_progress >= 0.1:
            mw.taskman.run_on_main(
                lambda: mw.progress.update(
                    label=f"{cnt} / {total} cards updated",
                    value=cnt,
                    max=total,
                )
            )
            last_progress = time.time()

        note = mw.col.getNote(nid)

        if audio_fld in note:
            # IMPORTANT: BEFORE DOWNLOADING, SLEEP FOR SET TIME IF APPLICABLE
            if sleep_time > 0:
                time.sleep(sleep_time)

            note_dict = {}
            for key, value in note.items():
                if key == filter_kana_fld:  # If '(None)' then it shouldn't find it anyway (unless someone has that as their field name for some reason)
                    value = filter_kana(value)
                note_dict.update({key: value})

            audio_filename = ad.download_single(note_dict, duplicate_fld)
            if audio_filename:
                note[audio_fld] = '[sound:' + audio_filename + ']'
                note.flush()
            cnt += 1

        if mw.progress.want_cancel():
            break

    return browser, cnt


def _processNotesOnSuccess(browser_cnt_tuple):
    """
    On success function for the _processNotes function
    Resets necessary items and displays a tooltip of the amount of notes updated
    """
    browser = browser_cnt_tuple[0]
    cnt = browser_cnt_tuple[1]
    browser.model.endReset()
    mw.requireReset()
    mw.progress.finish()
    mw.reset()
    tooltip("<b>Updated</b> {0} notes.".format(cnt), parent=browser)


def filter_kana(string):
    """
    Use a Regex filter to only return the hiragana from a string
    """
    hiragana_full = r'[ぁ-ゟ]'
    return ''.join(re.findall(hiragana_full, string))


def onBulkGenerate(browser):
    """
    CREDIT TO Batch Editing ADDON https://ankiweb.net/shared/info/291119185
    Modified slightly to work for this addon instead
    """
    nids = browser.selectedNotes()
    if not nids:
        tooltip("No cards selected.")
        return
    dialog = BulkGenerateDialog(browser, nids)
    dialog.exec()


def setupMenu(browser):
    """
    CREDIT TO Batch Editing ADDON https://ankiweb.net/shared/info/291119185
    Modified slightly to work for this addon instead
    """
    menu = browser.form.menuEdit
    menu.addSeparator()
    a = menu.addAction('Generate Bulk Audio...')
    a.setShortcut(QKeySequence("Ctrl+Alt+B"))
    a.triggered.connect(lambda _, b=browser: onBulkGenerate(b))


addHook("browser.setupMenus", setupMenu)
