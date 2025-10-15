#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gtk
import sys

PLUGIN_PROC = "project-egg-change-card-text"
PLUGIN_BINARY = "project-egg-change-card-text.py"

def change_text(image, layer, new_text):
	Gimp.get_pdb().run_procedure("gimp-text-layer-set-text", [image, layer, new_text])

def change_card_text_run(procedure, run_mode, image, drawables, config, data):
	if len(drawables) > 1:
		return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR,
			GLib.Error(f"Procedure '{PLUGIN_PROC}' works with zero or one layer."))
	elif len(drawables) == 1:
		if not isinstance(drawables[0], Gimp.Layer):
			return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR,
				GLib.Error(f"Procedure '{PLUGIN_PROC}' works with layers only."))

	if run_mode == Gimp.RunMode.INTERACTIVE:
		GimpUi.init(PLUGIN_BINARY)

		dialog = GimpUi.ProcedureDialog.new(procedure, config, "Change Card Text")
		dialog.fill(["new-name", "new-type", "new-effect", "new-cost", "new-draw", "new-discard", "new-mill", "new-gold"])
		if not dialog.run():
			dialog.destroy()
			return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, None)
		else:
			dialog.destroy()

	# Run procedure
	new_name = config.get_property('new-name')
	new_type = config.get_property('new-type')
	new_effect = config.get_property('new-effect')
	new_cost = config.get_property('new-cost')
	new_draw = config.get_property('new-draw')
	new_discard = config.get_property('new-discard')
	new_mill = config.get_property('new-mill')
	new_gold = config.get_property('new-gold')

	input_layer = drawables[0]
	# Gimp.message("Found parent {}".format(parent.get_name()))
	# root = parent.get_parent()
	# Gimp.message("Parent has parent {}".format(root.get_name()))

	# input_layer = None
	# for layer in parent.get_children():
	# 	Gimp.message("Found child {}".format(layer.get_name()))
	# message = ", ".join([layer.get_name() for layer in parent.get_children()])
	# Gimp.message("Image has layers [{}]".format(message))
	# for layer in parent.get_children():
	# 	if layer.get_name() == "InputText":
	# 		input_layer = layer
	# 		break

	if not input_layer:
		Gimp.message("Did not find InputText layer")
		return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR, 
			GLib.Error(f"Procedure {PLUGIN_PROC} needs an 'InputText' layer to work."))

	image.undo_group_start()
	for child in input_layer.get_children():
		if not isinstance(child, Gimp.TextLayer):
			continue
		
		layer_name = child.get_name()
		if layer_name == "Name":
			child.set_text(new_name)
			# change_text(input_layer, child, new_name)
		elif layer_name == "Type":
			child.set_text(new_type)
			# change_text(input_layer, child, new_type)
		elif layer_name == "Effect":
			child.set_text(new_effect)
			# change_text(input_layer, child, new_effect)
		elif layer_name == "CostNum":
			child.set_text(new_cost)
			# change_text(input_layer, child, new_cost)
		elif layer_name == "DrawNum":
			child.set_text(new_draw)
			# change_text(input_layer, child, new_draw)
		elif layer_name == "DiscardNum":
			child.set_text(new_discard)
			# change_text(input_layer, child, new_discard)
		elif layer_name == "MillNum":
			child.set_text(new_mill)
			# change_text(input_layer, child, new_mill)
		elif layer_name == "GoldNum":
			child.set_text(new_gold)
			# change_text(input_layer, child, new_gold)

	image.undo_group_end()
	Gimp.displays_flush()

	return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)

class ChangeCardText(Gimp.PlugIn):
	def do_query_procedures(self):
		return [ PLUGIN_PROC ]

	def do_create_procedure(self, name):
		procedure = None

		if name != PLUGIN_PROC:
			return None

		procedure = Gimp.ImageProcedure.new(self, name,
			Gimp.PDBProcType.PLUGIN,
			change_card_text_run, None)
		procedure.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.DRAWABLE)
		procedure.set_menu_label("_Change Card Text")
		procedure.set_attribution("MCKoleman", "MCKoleman, Project Egg", "2025")
		procedure.add_menu_path("<Image>/Project Egg")
		procedure.set_documentation("Change text of card text layers",
			"Changes the text in the card InputText layers",
			None)

		procedure.add_string_argument("new-name", "Name", None, "Name",
			GObject.ParamFlags.READWRITE)
		procedure.add_string_argument("new-type", "Type", None, "Type",
			GObject.ParamFlags.READWRITE)
		procedure.add_string_argument("new-effect", "Effect", None, "-",
			GObject.ParamFlags.READWRITE)
		procedure.add_string_argument("new-cost", "Cost", None, "0",
			GObject.ParamFlags.READWRITE)
		procedure.add_string_argument("new-draw", "Draw", None, "0",
			GObject.ParamFlags.READWRITE)
		procedure.add_string_argument("new-discard", "Discard", None, "0",
			GObject.ParamFlags.READWRITE)
		procedure.add_string_argument("new-mill", "Mill", None, "0",
			GObject.ParamFlags.READWRITE)
		procedure.add_string_argument("new-gold", "Gold", None, "0",
			GObject.ParamFlags.READWRITE)
		return procedure

Gimp.main(ChangeCardText.__gtype__, sys.argv)