import click
import pendulum
from pprint import pprint
from jira.exceptions import JIRAError
from majira.main import main, get_api, MajiraError
from majira.utils import panic, warning


@main.command()
@click.option('--mine', help="Include your tickets", is_flag=True)
@click.argument('template')
@click.pass_context
def list(ctx, mine, template):
    """List Jira tickets from JQL query"""
    
    username = ctx.obj.username
    api = ctx.obj.api

    query = ctx.obj.dashboards.get(template)
    if query is None:
        panic("Cannot find the specified JQL template '%s' in your config" % template)

    if mine:
        query += ' AND (assignee = %s OR assignee is EMPTY) ' % username
    else:
        query += ' AND assignee is EMPTY '

    query += 'ORDER BY summary ASC, created DESC, Rank ASC'

    issues = api.search_issues(query)
    for issue in issues:
        created = pendulum.parse(issue.fields.created)
        updated = pendulum.parse(issue.fields.updated)
        click.echo("%s: %s (%s) [created:%s, updated:%s]" % (
            issue.key, issue.fields.summary, issue.fields.status.name,
            created.to_day_datetime_string(), updated.to_day_datetime_string()))


def to_progress(api, issue, assignee=None):
    t = api.find_transitionid_by_name(issue, 'In Progress')
    if not t:
        raise MajiraError("Can't transition to 'In Progress' for %s" % issue)

    if assignee:
        api.assign_issue(issue, assignee)
    api.transition_issue(issue, t)


def to_resolved(api, issue, assignee=None):
    t = api.find_transitionid_by_name(issue, 'Resolved')
    if not t:
        raise MajiraError("Can't transition to 'Resolved' for %s" % issue)

    if assignee:
        api.assign_issue(issue, assignee)
    api.transition_issue(issue, t, resolution={ 'name': 'Fixed' })


# TODO: use Jinja templates to create several tickets at once
@main.command()
@click.option('--project', type=click.Choice(['OP']), help="Specify the Jira Project",
              default='OP')
@click.option('--category', default='Task', help="Specify the issue category")
@click.option('--assign', help="Assign the issue to someone")
def create(project, category, assign):
    """Open $EDITOR with a template and create a ticket"""

    contents = click.edit("TITLE\n\nDESCRIPTION\n")
    if contents is None:
        panic("No contents provided")

    contents = contents.strip(" \n")

    lines = contents.split('\n')
    title = lines.pop(0)
    description = '\n'.join(lines)
    description = description.strip(" \n")

    click.echo("Ticket preview:\nTitle: %s\nDescription:\n%s\n" % (title, description))
    if not click.confirm("Really create ticket?"):
        return

    api = get_api()
    issue = api.create_issue(project=project, summary=title, description=description,
                             issuetype={ 'name': category })
    click.echo("Created issue %s" % issue.key)

    if assign:
        api.assign_issue(issue, assign)
        click.echo("Issue assigned to %s" % assign)


@main.command()
@click.option('--assign', help="Assign the issue to a user")
@click.option('--comment', help="Add a comment to the issue")
@click.argument('issue_id')
def closefix(assign, comment, issue_id):
    """Mark a OP ticket as Closed (Resolved)"""

    api = get_api()
    try:
        issue = api.issue(issue_id)
    except JIRAError as ex:
        panic("Can't find issue %s (%s)" % (issue_id, ex.text))

    status = issue.fields.status.name

    try:
        if status == 'To Do Later':
            to_progress(api, issue, assign)
            to_resolved(api, issue, assign)
        elif status == 'In Progress':
            to_resolved(api, issue, assign)
        else:
            click.echo("Won't touch issue with status '%s'" % status)
            return

        if comment:
            api.add_comment(issue.key, comment)

    except MajiraError as ex:
        panic(str(ex))
    else:
        click.echo("Issue %s resolved and closed" % issue_id)
