from PyQt5.QtWidgets import QListWidgetItem
import re

class RawTextItem (QListWidgetItem):

    formattedText = ""
    text = ""
    sticky = False
    
    def __init__(self, formattedText, source, sticky, parent = None):
        self.sticky = sticky
        # take "formattedText" and remove the formatting so it looks coherent on the UI list
        self.formattedText = formattedText
        self.text = re.sub(r'>[\n\r\s]+<', r'><', formattedText, flags=re.S)
        self.text = re.search(r'(<body.*?/body>)', self.text, flags=re.S)
        self.text = self.text.group(1)
        self.text = re.sub(r'<.*?>', r'', self.text, flags=re.S)
        prefix = source + (" sticky" if sticky else "")
        self.text = "[%s] %s" % (prefix, self.text)
        # initialize this item's parameters
        super(RawTextItem, self).__init__(self.text, parent)
        