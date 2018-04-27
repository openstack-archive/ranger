#!/usr/bin/python
import argparse
from orm.orm_client.ormcli import cmscli
from orm.orm_client.ormcli import fmscli
from orm.orm_client.ormcli import imscli
from orm.orm_client.ormcli import rmscli
import sys


class Cli:
    def create_parser(self):
        self.parser = argparse.ArgumentParser(prog='orm',
                                              description='ORM REST CLI')
        service_sub = self.parser.add_subparsers(dest='service',
                                                 metavar='<service>')
        self.submod = {'cms': cmscli, 'fms': fmscli, 'ims': imscli,
                       'rms': rmscli}
        for s in self.submod.values():
            s.add_to_parser(service_sub)

    def parse(self, argv=sys.argv):
        sys.argv = argv
        self.args = self.parser.parse_args()

    def logic(self):
        self.submod[self.args.service].run(self.args)


def main(argv):
    cli = Cli()
    cli.create_parser()
    cli.parse(argv)
    cli.logic()


if __name__ == "__main__":
    main(sys.argv)
