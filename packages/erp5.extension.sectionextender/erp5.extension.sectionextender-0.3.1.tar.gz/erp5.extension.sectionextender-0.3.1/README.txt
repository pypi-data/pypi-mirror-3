A buildout extension to allow any section of 'parts' to define options
which will be appended to an option of another section.

Example configuration
---------------------

[buildout]
extensions = erp5.extension.sectionextender

section-extender =
  supervisor-instance:programs supervisor-program

parts =
  supervisor-instance
  test1-instance
  test3-instance

[supervisor-instance]
recipe = collective.recipe.supervisor

[test1-instance]
recipe = recipe.foo.bar
supervisor-program = 21 test1-instance test1-instance

[test2-instance]
recipe = recipe.foo.bar2
supervisor-program = 22 test2-instance test2-instance

[test3-instance]
recipe = recipe.foo.bar3
supervisor-program = 23 test3-instance test3-instance


With this configuration, 'supervisor-program' options in
'test1-instance' and 'test3-instance' will be added to
'${supervisor-instance:programs}', but not 'test2-instance' as it's
not in 'parts'.

You can specify several sections to be extended by just adding them to
'section-extender' (one per line).
