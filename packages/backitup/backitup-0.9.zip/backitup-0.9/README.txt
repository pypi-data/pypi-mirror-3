`backitup` is a module for easily backing up files.
It is designed for ease of use for python programmers,
by doing a few simple things clearly.

General Use
&&&&&&&&&&&

- Create the python file that will call backitup.
  Generally this will hard-code some configuration information,
  such as the backup directory, source file paths, etc.
  It can also do stuff like configure logging.
- This python file should generally also create the upload
  handlers (make_upload_*).
- Your python file invokes backitup.create_archive.
- It takes the result of create_archive and passes
  it and the upload handlers to upload_all.

See the included `examples` directory for a set of example files,
which is similar to how things are set up on the author's machine.

Notes
&&&&&

All 'configuration' is handled by passing arguments into the functions.
The module-level constants are for defining default values only.
You should never need to change these consts, just provide different args.

`backitup` does not come with a commandline interface.
Call me a heretic but I'd rather write a clear API that can
be called from python, and let you write a wrapper for it
that you can invoke with YOUR own CLI.

Running multiple backups at the same time may produce some
unexpected race conditions, with regards to backup
pruning, and myphp backup.
