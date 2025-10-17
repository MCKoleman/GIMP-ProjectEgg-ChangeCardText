#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import no_type_check
import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp #type: ignore
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi #type: ignore
from gi.repository import GObject #type: ignore
from gi.repository import GLib #type: ignore
from gi.repository import Gtk #type: ignore
import sys
import re

PLUGIN_PROC = "project-egg-change-card-text"
PLUGIN_BINARY = "project-egg-change-card-text.py"

@no_type_check
def parse_content_text(content: str):
	match = re.search(
		r'^(?P<name>[^,]*),[\s]*(?P<cost>[\d]*)/(?P<draw>[\d]*)/(?P<discard>[\d]*)/(?P<mill>[\d]*)/(?P<gold>[\d]*)[\s]*(-[\s]*(?P<type>[^:]*)(:[\s]*(?P<effect>.*).*)?)?$', 
		content
	)

	# Return default if there was no match
	if not match:
		return ("", "", "", "", "", "", "", "")

	return (
		match.group("name"), 
		match.group("type") or "Basic", 
		match.group("effect") or "-", 
		match.group("cost"), 
		match.group("draw"), 
		match.group("discard"), 
		match.group("mill"), 
		match.group("gold")
	)



@no_type_check
def get_layer_name(name: str):
	return name.split(" #")[0]



@no_type_check
def change_card_text(layer, content: str, version: str):
	# Parse card definition into its text
	(new_name, new_type, new_effect, 
		new_cost, new_draw, new_discard, new_mill, new_gold
	) = parse_content_text(content)

	for child in layer.get_children():
		if not isinstance(child, Gimp.TextLayer):
			continue
		
		layer_name = get_layer_name(child.get_name())
		if layer_name == "Name":
			child.set_text(new_name)
		elif layer_name == "Type":
			child.set_text(new_type)
		elif layer_name == "Effect":
			child.set_text(new_effect)
		elif layer_name == "CostNum":
			child.set_text(new_cost)
		elif layer_name == "DrawNum":
			child.set_text(new_draw)
		elif layer_name == "DiscardNum":
			child.set_text(new_discard)
		elif layer_name == "MillNum":
			child.set_text(new_mill)
		elif layer_name == "GoldNum":
			child.set_text(new_gold)
		elif layer_name == "Version":
			child.set_text(version)
	return


@no_type_check
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
		dialog.fill(["content", "num-cards", "version"])
		if not dialog.run():
			dialog.destroy()
			return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, None)
		else:
			dialog.destroy()

	# Run procedure
	root = drawables[0]
	content = config.get_property('content')
	num_cards = config.get_property('num-cards')
	version = config.get_property('version')
	content_lines = list(filter(lambda line: line != "", content.split("\n")))[:num_cards]
	
	# Loop through all cards in root ("Cards" layer)
	image.undo_group_start()
	for [index, card] in enumerate(root.get_children()):
		# Find "InputText #(num)" layer for each Card
		for card_layer in card.get_children():
			card_layer_name = get_layer_name(card_layer.get_name())
			
			# Skip all layers except InputText
			if card_layer_name != "InputText":
				continue

			card_content = content_lines[index] if index < len(content_lines) else ""
			change_card_text(card_layer, card_content, version)

	image.undo_group_end()
	Gimp.displays_flush()

	return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)



class ChangeCardText(Gimp.PlugIn): #type: ignore
	def do_query_procedures(self):
		return [ PLUGIN_PROC ]

	@no_type_check
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

		procedure.add_string_argument("content", "Content", None, "Name, 0/0/0/0/0 - Play: Effect.",
			GObject.ParamFlags.READWRITE)
		procedure.add_int_argument("num-cards", "Number of Cards", None, 0, 20, 9,
			GObject.ParamFlags.READWRITE)
		procedure.add_string_argument("version", "Version", None, "1",
			GObject.ParamFlags.READWRITE)
		return procedure



Gimp.main(ChangeCardText.__gtype__, sys.argv) #type: ignore