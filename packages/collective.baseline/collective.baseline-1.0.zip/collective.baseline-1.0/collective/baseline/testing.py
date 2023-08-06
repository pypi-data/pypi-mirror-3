from plone.testing import z2

from plone.app.testing import *
import collective.baseline

FIXTURE = PloneWithPackageLayer(zcml_filename="configure.zcml",
                                zcml_package=collective.baseline,
                                additional_z2_products=[],
                                gs_profile_id='collective.baseline:default',
                                name="collective.baseline:FIXTURE")

INTEGRATION = IntegrationTesting(bases=(FIXTURE,),
                        name="collective.baseline:Integration")

FUNCTIONAL = FunctionalTesting(bases=(FIXTURE,),
                        name="collective.baseline:Functional")

