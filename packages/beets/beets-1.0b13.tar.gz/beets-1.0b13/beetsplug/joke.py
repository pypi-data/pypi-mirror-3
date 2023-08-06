from beets import mediafile, plugins, ui

class JokePlugin(plugins.BeetsPlugin):
    def item_fields(self):
        return {
            'foo': mediafile.MediaField(
                mp3 = mediafile.StorageStyle(
                    'TXXX', id3_desc=u'Foo Field'),
                mp4 = mediafile.StorageStyle(
                    '----:com.apple.iTunes:Foo Field'),
                etc = mediafile.StorageStyle('FOO FIELD')
            ),
        }

    def commands(self):
        cmd = ui.Subcommand('foo', help='show foo')
        def func(lib, config, opts, args):
            path = args[0]
            f = mediafile.MediaFile(path)
            print 'foo is:', f.foo
            f.foo = args[1]
            f.save()
        cmd.func = func
        return [cmd]
