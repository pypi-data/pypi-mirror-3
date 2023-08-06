from plone.testing import z2

from plone.app.testing import *
import collective.metarobots

FIXTURE = PloneWithPackageLayer(zcml_filename="configure.zcml",
                                zcml_package=collective.metarobots,
                                additional_z2_products=[],
                                gs_profile_id='collective.metarobots:default',
                                name="collective.metarobots:FIXTURE")

INTEGRATION = IntegrationTesting(bases=(FIXTURE,),
                        name="collective.metarobots:Integration")

FUNCTIONAL = FunctionalTesting(bases=(FIXTURE,),
                        name="collective.metarobots:Functional")

