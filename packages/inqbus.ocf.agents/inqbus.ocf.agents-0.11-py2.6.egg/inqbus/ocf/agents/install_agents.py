import os
import pkg_resources


def install():
    group = 'console_scripts'
    import pdb; pdb.set_trace()
    for entrypoint in pkg_resources.iter_entry_points(group=group):
        # Grab the function that is the actual plugin.
        plugin = entrypoint.load()
        # Call the plugin (and zest.releaser wants to pass one
        # data item: modify to suit your own API).




def main():
    """
    Entry point for the python console scripts
    """

    install()
#    import sys
#    OpenVPN().run(sys.argv)

if __name__ == "__main__":
    main()
