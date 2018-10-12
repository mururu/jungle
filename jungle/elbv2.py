# -*- coding: utf-8 -*-
import click
from botocore.exceptions import ClientError
from jungle.session import create_session


@click.group()
@click.option('--profile-name', '-P', default=None, help='AWS profile name')
@click.pass_context
def cli(ctx, profile_name):
    """ELBv2 CLI group"""
    ctx.obj = {'AWS_PROFILE_NAME': profile_name}


@cli.command(help='List ELBv2 instances')
@click.argument('name', default='*')
@click.option('--list-instances', '-l', 'list_instances', is_flag=True, help='List attached EC2 instances')
@click.pass_context
def ls(ctx, name, list_instances):
    """List ELBv2 instances"""
    session = create_session(ctx.obj['AWS_PROFILE_NAME'])

    client = session.client('elbv2')
    inst = {'LoadBalancerDescriptions': []}
    if name == '*':
        inst = client.describe_load_balancers()
    else:
        try:
            inst = client.describe_load_balancers(LoadBalancerNames=[name])
        except ClientError as e:
            click.echo(e, err=True)

    for i in inst['LoadBalancers']:
        click.echo(i['LoadBalancerName'])
        if list_instances:
            inst2 = client.describe_target_groups(LoadBalancerArn=i['LoadBalancerArn'])
            for i2 in inst2['TargetGroups']:
                click.echo('\t{0}'.format(i2['TargetGroupName']))
                inst3 = client.describe_target_health(TargetGroupArn=i2['TargetGroupArn'])
                for i3 in inst3['TargetHealthDescriptions']:
                    click.echo('\t\t{0}\t{1}'.format(i3['Target']['Id'], i3['TargetHealth']['State']))
