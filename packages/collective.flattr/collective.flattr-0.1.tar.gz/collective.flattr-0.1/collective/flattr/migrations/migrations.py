import logging

logger = logging.getLogger('collective.flattr.migrations.migrations')


def migrate_1000_1001(portal_setup):
    """ Doing nothing. Here the profile-collective.flattr:migrate_1000_1001
    should be imported
    """
    logger.info('Running all import steps from collective.flattr:migration_1000_1001')
    portal_setup.runAllImportStepsFromProfile('profile-collective.flattr:migration_1000_1001')
    return
