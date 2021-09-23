# Layton Event Editor

THIS EDITOR IS NO LONGER MANTAINED NOR WORK IS BEING MADE. Instead, visit https://github.com/thatrandomstranger/LaytonEditor.

This is an editor made ONLY to edit events of the 2nd Professor Layton.

### Setup
Just install requirements.txt. If you want to use the original fonts for the game (the
only ones that look good lol), you should export them from the original game using Tkinter
with encoding utf-8, and then convert them to json ~~as I've been too lazy to write it to
work with xml for now~~.

### Usage
To start an event just modify the event id on `main.py`. To run the editor, just execute
`main.py`.

Once it the editor, you will be presented with four windows. The first one is the preview
of the event and is situated in the top left corner. To it's right, you will find the event
flow, or just the nodes of the event. In the bottom left corner there is the filesystem which
you can explore and preview images. Currently, .arj images are not previewed.

Using the event flow you can click on any node to preview the state of the game when it's
executed. You can drag nodes around and if you click were there are no nodes you can move
the camera that is viewing the nodes.

If you wish to continue execution when you've clicked on a node, press 'C'. If you wish to
run the editor from start, press 'R'.

Right now events can't be modified (ironically it's an editor).
