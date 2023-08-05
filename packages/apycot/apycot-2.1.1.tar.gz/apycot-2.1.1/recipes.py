def create_quick_recipe(session):
    recipe = session.create_entity('Recipe', name=u'apycot.recipe.quick')
    init = recipe.add_step(u'action', u'apycot.init', initial=True)
    getdeps = init.add_next_step(u'action', u'apycot.get_dependancies')
    checkout = getdeps.add_next_step(u'action', u'apycot.checkout', for_each=u'projectenv')
    install = checkout.add_next_step(u'action', u'apycot.install', for_each=u'projectenv')
    pyunit = install.add_next_step(u'action', u'apycot.pyunit', final=True)

def create_full_recipe(session):
    recipe = session.create_entity('Recipe', name=u'apycot.recipe.full')
    init = recipe.add_step(u'action', u'apycot.init', initial=True)
    getdeps = init.add_next_step(u'action', u'apycot.get_dependancies')
    checkout = getdeps.add_next_step(u'action', u'apycot.checkout', for_each=u'projectenv')
    install = checkout.add_next_step(u'action', u'apycot.install', for_each=u'projectenv')
    pylint = recipe.add_step(u'action', u'apycot.pylint')
    pyunit = recipe.add_step(u'action', u'apycot.pyunit',
                             arguments=u'EnsureOptions(pycoverage=True)')
    recipe.add_transition(install, (pylint, pyunit))
    pycoverage = pyunit.add_next_step(u'action', u'apycot.pycoverage')
    recipe.add_transition((pylint, pycoverage),
                          recipe.add_step(u'action', u'basic.noop', final=True))
    return recipe

def create_debian_recipe(session):
    recipe = session.create_entity('Recipe', name=u'apycot.recipe.debian')
    step1 = recipe.add_step(u'action', u'apycot.init', initial=True)
    step2 = recipe.add_step(u'action', u'apycot.checkout')
    step3 = recipe.add_step(u'action', u'apycot.lgp.check')
    step3bis = recipe.add_step(u'action', u'apycot.lgp.build')
    step4 = recipe.add_step(u'action', u'apycot.lintian')
    step5 = recipe.add_step(u'action', u'basic.noop', final=True)
    recipe.add_transition(step1, step2)
    recipe.add_transition(step2, (step3, step3bis))
    recipe.add_transition(step3bis, step4)
    recipe.add_transition((step3, step4), step5)
    return recipe

def create_experimental_recipe(session):
    recipe = session.create_entity('Recipe', name=u'apycot.recipe.experimental')
    step1 = recipe.add_step(u'recipe', u'apycot.recipe.debian', initial=True)
    step2 = recipe.add_step(u'action', u'apycot.ldi.upload')
    step3 = recipe.add_step(u'action', u'apycot.ldi.publish', final=True)
    recipe.add_transition(step1, step2)
    recipe.add_transition(step2, step3)
    return recipe

# def create_publish_recipe(session):
#     # XXX
#     # copy/upload from logilab-experimental to logilab-public
#     # example: ldi upload logilab-public /path/to/experimental/repo/dists/*/*.changes
#     recipe = session.create_entity('Recipe', name=u'apycot.recipe.publish')
#     return recipe
