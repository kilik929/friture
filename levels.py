#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timoth?Lecomte

# This file is part of Friture.
#
# Friture is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# Friture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Friture.  If not, see <http://www.gnu.org/licenses/>.

from PyQt4 import QtCore, QtGui
from numpy import log10, abs
import levels_settings # settings dialog
from qsynthmeter import qsynthMeter
import audioproc

STYLESHEET = """
qsynthMeter {
border: 1px solid gray;
border-radius: 2px;
padding: 1px;
}
"""

SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25
SAMPLING_RATE = 44100

class Levels_Widget(QtGui.QWidget):
	def __init__(self, parent = None, logger = None):
		QtGui.QWidget.__init__(self, parent)
		self.setObjectName("Levels_Widget")
		
		self.gridLayout = QtGui.QGridLayout(self)
		self.gridLayout.setObjectName("gridLayout")
		self.label_rms = QtGui.QLabel(self)
		font = QtGui.QFont()
		font.setPointSize(14)
		font.setWeight(75)
		font.setBold(True)
		self.label_rms.setFont(font)
		self.label_rms.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing)
		self.label_rms.setObjectName("label_rms")
		self.gridLayout.addWidget(self.label_rms, 0, 0, 1, 1)
		self.meter = qsynthMeter(self)
		self.meter.setStyleSheet(STYLESHEET)
		self.meter.setObjectName("meter")
		self.gridLayout.addWidget(self.meter, 0, 1, 2, 1)
		self.label_peak = QtGui.QLabel(self)
		self.label_peak.setFont(font)
		self.label_peak.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
		self.label_peak.setObjectName("label_peak")
		self.gridLayout.addWidget(self.label_peak, 0, 2, 1, 1)
		self.label_rms_legend = QtGui.QLabel(self)
		self.label_rms_legend.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop|QtCore.Qt.AlignTrailing)
		self.label_rms_legend.setObjectName("label_rms_legend")
		self.gridLayout.addWidget(self.label_rms_legend, 1, 0, 1, 1)
		self.label_peak_legend = QtGui.QLabel(self)
		self.label_peak_legend.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
		self.label_peak_legend.setObjectName("label_peak_legend")
		self.gridLayout.addWidget(self.label_peak_legend, 1, 2, 1, 1)

		self.label_rms.setText("-100.0")
		self.label_peak.setText("-100.0")
		self.label_rms_legend.setText("dBFS\n RMS")
		self.label_peak_legend.setText("dBFS\n peak")
		#self.label_rms.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
		#self.label_rms_legend.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
		#self.label_peak.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
		#self.label_peak_legend.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
		
		# store the logger instance
		if logger is None:
		    self.logger = parent.parent.logger
		else:
		    self.logger = logger

		self.audiobuffer = None
		
		# initialize the settings dialog
		self.settings_dialog = levels_settings.Levels_Settings_Dialog(self, self.logger)
		
		# initialize the class instance that will do the fft
		self.proc = audioproc.audioproc(self.logger)

	# method
	def set_buffer(self, buffer):
		self.audiobuffer = buffer

	# method
	def update(self):
		if not self.isVisible():
			return
		
		# for slower response, we need to implement a low-pass filter here. 
		
		time = SMOOTH_DISPLAY_TIMER_PERIOD_MS/1000.
		floatdata = self.audiobuffer.data(time*SAMPLING_RATE)
		
		level_rms = 10*log10((floatdata**2).sum()/len(floatdata)*2. + 0*1e-80) #*2. to get 0dB for a sine wave
		level_max = 20*log10(abs(floatdata).max() + 0*1e-80)
		self.label_rms.setText("%.01f" % level_rms)
		self.label_peak.setText("%.01f" % level_max)
		self.meter.setValue(0, level_rms)
		self.meter.setValue(1, level_max)
		
		if 0:
			fft_size = time*SAMPLING_RATE #1024
			maxfreq = SAMPLING_RATE/2
			sp, freq, A, B, C = self.proc.analyzelive(floatdata, fft_size, maxfreq)
			print level_rms, 10*log10((sp**2).sum()*2.), freq.max()

	# slot
	def settings_called(self, checked):
		self.settings_dialog.show()

	# method
	def saveState(self, settings):
		self.settings_dialog.saveState(settings)
	
	# method
	def restoreState(self, settings):
		self.settings_dialog.restoreState(settings)