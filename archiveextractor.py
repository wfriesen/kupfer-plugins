__kupfer_name__ = _("Archive Extractor")
__kupfer_sources__ = ()
__kupfer_text_sources__ = ()
__kupfer_actions__ = (
		"UnpackTo",
		)
__description__ = _("Extract archives in Kupfer")
__version__ = ""
__author__ = "William Friesen <wfriesen@gmail.com>"

import os
import zipfile, tarfile

from kupfer.objects import Action, FileLeaf
from kupfer import pretty
from kupfer import task, uiutils
from kupfer import plugin_support
import rarfile

class UnpackTask(task.ThreadTask):
	def __init__(self, archive_name, extract_path):
		super(task.Task, self).__init__()
		self.archive_name = archive_name
		self.extract_path = extract_path
		self.error = None

	def thread_do(self):
		if zipfile.is_zipfile(self.archive_name):
			open_func = zipfile.ZipFile
		elif tarfile.is_tarfile(self.archive_name):
			open_func = tarfile.open
		elif rarfile.is_rarfile(self.archive_name):
			open_func = rarfile.RarFile
		else:
			self.error = "Bad archive: %s" % self.archive_name
			return
		archive = open_func(self.archive_name)
		for name in archive.namelist():
			potential = os.path.join(self.extract_path,name)
			if os.path.exists(potential):
				self.error = "File: %s exists" % potential
				return
			archive.extract(name,self.extract_path)

	def thread_finish(self):
		if self.error:
			title = "Error"
			message = self.error
		else:
			title = "Extraction Complete"
			message = "Extracted\n%s\nto\n%s" %	(self.archive_name, self.extract_path)
		uiutils.show_notification(title, message)

class UnpackTo (Action):
	def __init__(self):
		Action.__init__(self, _("Extract To..."))
		# Set standard way to access different archive types
		tarfile.TarFile.namelist = tarfile.TarFile.getnames

	def is_async(self):
		return True

	def activate(self, leaf, obj):
		return UnpackTask(leaf.object,obj.object)

	def item_types(self):
		yield FileLeaf

	def valid_for_item(self, item):
		if not os.path.isdir(item.object):
			return (zipfile.is_zipfile(item.object) or
				tarfile.is_tarfile(item.object) or
				rarfile.is_rarfile(item.object))

	def requires_object(self):
		return True

	def object_types(self):
		yield FileLeaf

	def valid_object(self, obj, for_item):
		return os.path.isdir(obj.object)

	def get_description(self):
		return _("Extract compressed archive to a given location")
