PROFILE_ID = 'profile-zest.emailhider:default'


def install_pyproxy(context):
    # This is a new dependency.
    context.runAllImportStepsFromProfile('profile-jquery.pyproxy:default')


def run_kss_step(context):
    context.runImportStepFromProfile(PROFILE_ID, 'kssregistry')


def run_javascript_step(context):
    context.runImportStepFromProfile(PROFILE_ID, 'jsregistry')


def run_browserlayer_step(context):
    context.runImportStepFromProfile(PROFILE_ID, 'browserlayer')
