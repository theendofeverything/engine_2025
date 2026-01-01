# Pygame Docs

* `;kpg` opens the local copy of the pygame docs in your browser (must activate
  the virtual environment where `pygame` is installed before launching Vim)
* `;KPG` opens the on-line copy of the pygame docs
* `;kpy` opens the local copy of the Python docs in your browser (must download
  the HTML Python docs manually, see my notes in `:h python.txt`)
* `;KPY` opens the on-line copy of the Python docs

## Details on opening pygame docs

Open `pygame/docs/generated/index.html` in your browser:

```vim
" This works if you added your virtualenv site-packages folder to your Vim path
:find pygame/docs/generated/index.html
" Now with the cursor in the buffer, use Vim shortcut ;html
```

From the command-line, `cd` into the virtualenv site-packages folder, then:

```
$ open pygame/docs/generated/index.html
```

Or use `pydoc` to open specific functions in your MANPAGER (my MANPAGER is Vim):

```
$ pydoc3 pygame
...
$ pydoc3 pygame.display
...
$ pydoc3 pygame.display.set_mode
```


