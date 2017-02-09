import sys
import click


def panic(message):
    click.echo("%s: %s" % (click.style('ERROR', fg='red'), message), err=True)
    sys.exit(1)


def warning(message):
    click.echo("%s: %s" % (click.style('WARNING', fg='yellow'), message), err=True)


def validate_op_issue(ctx, param, value):
    if not value.startswith('OP-'):
        raise click.BadParameter("Issue must be from project Operations (OP-XXXXX)")
    return value
