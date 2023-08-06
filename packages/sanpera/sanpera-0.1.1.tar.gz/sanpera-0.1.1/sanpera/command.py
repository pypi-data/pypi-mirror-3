"""Python reimplementations of the ImageMagick command-line tools."""

from sanpera.image import Image

class CommandLineArgumentError(ValueError): pass

def convert(arguments):
    """Equivalent to ImageMagick's `convert` program.

    Arguments should be an iterable; this function expects shell parsing and
    splitting to have been performed already.
    """

    images = []
    args = deque(arguments)

    while args:
        arg = args.popleft()

        if not arg:
            raise CommandLineArgumentError("Empty string found in arguments")

        if arg[0] in ('-', '+'):
            # This is a switch.  Do a thing.
            switch = arg[1:]

            if switch == 'resize':
                try:
                    switch_param = int(args.popleft())
                except ValueError:
                    raise CommandLineArgumentError("Couldn't parse {arg} {param}".format(arg=arg, param=switch_param))
                except IndexError:
                    raise CommandLineArgumentError("{arg} requires an argument".format(arg=arg))

                switch_param


        else:
            # Looks like a filename
            if ':' in arg:
                format, filename = arg.split(':', 1)
            else:
                format = None  # auto
                filename = arg

            image = Image.read(open(filename))
            images.append(image)
