from plone.testing import z2

from plone.app.testing import *
import collective.linguadomains

FIXTURE = PloneWithPackageLayer(zcml_filename="configure.zcml",
                                zcml_package=collective.linguadomains,
                                additional_z2_products=[],
                                gs_profile_id='collective.linguadomains:default',
                                name="collective.linguadomains:FIXTURE")

INTEGRATION = IntegrationTesting(bases=(FIXTURE,),
                        name="collective.linguadomains:Integration")

FUNCTIONAL = FunctionalTesting(bases=(FIXTURE,),
                        name="collective.linguadomains:Functional")

