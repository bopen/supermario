# -*- coding: utf-8 -*-

# python 2 support via python-future
from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import int

import click
import luigi

from mariobros import mario
from mariobros import mariofile as mariofile_


def mariobros(
        targets=('DEFAULT',), mariofile='mario.ini', print_ns=False, dry_run=False, workers=1,
        **kwargs
):
    """Main mariobros entry point. Parse the configuration file and launch the build of targets.

    :param sequence targets: List of targets.
    :param unicode mariofile: Mariofile name.
    :param bool print_ns: Flag to print namespace.
    :param bool dry_run: Dry run flag.
    :param int workers: Number of workers.
    :param dict kwargs: Passed to the luigi.build function.
    """
    if dry_run and workers > 1:
        workers = 1
        mario.LOGGER.warning('Dry run is incompatible with multiprocessing. Setting --workers=1')
    section_namespaces = mariofile_.parse_mariofile(mariofile)
    default_namespace, rendered_namespaces = mario.render_config(section_namespaces)
    if print_ns:
        namespaces = mario.print_namespaces(default_namespace, section_namespaces)
        print(namespaces)
    else:
        target_tasks = mario.mario(
            rendered_namespaces, default_namespace, targets=targets, dry_run=dry_run
        )
        luigi.build(target_tasks, workers=workers, **kwargs)


@click.command()
@click.argument('targets', nargs=-1, type=click.Path())
@click.option(
    '--file', '--mariofile', '-f', default='mario.ini',
    help='Main configuration file', type=click.Path(exists=True, dir_okay=False))
@click.option(
    '--logging_conf_file', default=None,
    help='Logging configuration file', type=click.Path(exists=True, dir_okay=False))
@click.option('--workers', default=1, help='Number of workers', type=int)
@click.option('--local-scheduler', is_flag=True)
@click.option('--print-ns', is_flag=True)
@click.option(
    '--dry-run', '-n', is_flag=True,
    help="Don't actually run any commands; just print them.")
def main(targets, **kwargs):
    if not targets:
        targets = ('DEFAULT',)
    mariobros(targets, **kwargs)
