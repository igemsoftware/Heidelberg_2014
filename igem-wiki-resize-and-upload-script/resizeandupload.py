import os, sys, glob
import pywikibot
import pywikibot.data.api
import Image
from pywikibot import config
from pywikibot.bot import QuitKeyboardInterrupt

class UploadRobot:
	def __init__(self, filename, upload_filename, description, site="test", ignoreWarning =True):
		self.filename = filename
		self.upload_filename = upload_filename
		self.description = description
		self.ignoreWarning = ignoreWarning

		self.targetSite = pywikibot.Site()
		self.targetSite.forceLogin()

	def upload_Image(self, debug=True):
		upload_filename = self.upload_filename
		site = self.targetSite
		imagepage = pywikibot.FilePage(site, upload_filename)
		imagepage.text = self.description
		pywikibot.output(u'Uploading file (%s => %s) to %s via API....' % (self.filename, upload_filename, site))

		try:
			site.upload(imagepage, source_filename=self.filename,
							ignore_warnings=self.ignoreWarning,
							chunk_size=0)

		except pywikibot.data.api.UploadWarning as warn:
			pywikibot.output(
				u'We got a warning message: {0}'.format(warn.message))
			if self.abort_on_warn(warn.code):
				answer = "N"
			else:
				answer = pywikibot.inputChoice(u"Do you want to ignore?",
											   ['Yes', 'No'], ['y', 'N'], 'N')
			if answer == "y":
				self.ignoreWarning = 1
				self.keepFilename = True
				return self.upload_image(debug)
			else:
				pywikibot.output(u"Upload aborted.")
				return
		except pywikibot.data.api.APIError as error:
			if error.code == u'uploaddisabled':
				pywikibot.error("Upload error: Local file uploads are disabled on %s."
								  % site)
			else:
				pywikibot.error("Upload error: ", exc_info=True)
		except Exception:
			pywikibot.error("Upload error: ", exc_info=True)

		else:
			# No warning, upload complete.
			pywikibot.output(u"Upload successful.")
			return upload_filename  # data['filename']


class UploadandResizeRoboter:
	def __init__(self, image, prefix="", tempdir="./temp/"):
		self.image = image
		self.prefix = prefix
		if not os.path.exists(tempdir):
			os.mkdir(tempdir)
		self.tempdir = tempdir
		if self.tempdir[-1] != "/":
			self.tempdir += "/"
		self.widths = { "full" : 1070, "half" : 780, "quarter" : 300}



	def resizeAndUploadImage(self):
		imgf = Image.open(self.image);
		basename = os.path.basename(self.image)
		orgfile = self.prefix + "orig_" + basename
		org_uploader = UploadRobot(self.image, orgfile, "Original File %s" % orgfile)
		org_uploader.upload_Image()

		for name, width in self.widths.items():
			print "Processing resize: %s => %i" % (name, width)
			cur_img = imgf.copy()
			size = cur_img.size
			ratio = width/float(size[0])
			print "Image size: (%i, %i), ratio: %f new size: (%i, %i)" % (int(size[0]*ratio), int(size[1]*ratio), ratio, size[0]*ratio, size[1]*ratio)
			cur_img.thumbnail((int(cur_img.size[0]*ratio), int(cur_img.size[1]*ratio)), Image.ANTIALIAS)

			tempfile = self.tempdir + name + "_" + basename
			cur_img.save(tempfile, "PNG")

			uploader = UploadRobot(tempfile, self.prefix + os.path.basename(tempfile), "Thumbnail (%ipx X %i px) of %s" % (size[0], size[1], orgfile))
			uploader.upload_Image()






resizeUploadBot = UploadandResizeRoboter(sys.argv[1], sys.argv[2], sys.argv[3])
resizeUploadBot.resizeAndUploadImage()

