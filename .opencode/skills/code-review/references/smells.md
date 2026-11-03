# Smell baseline

Reference for the code-review skill. Apply each smell as a labelled judgement
call, not a hard violation. A documented repository standard overrides this list;
skip anything tooling already enforces. Mark each finding **Optional** unless a
documented repo standard makes it **Required**.

## The smells

- **Mysterious name** - a name does not reveal what a function, variable, or type
  does or holds. Rename it; if no honest name comes, the design is murky.
- **Duplicated code** - the same logic shape appears in more than one hunk or
  file. Extract the shared shape and call it from both.
- **Feature envy** - a method reaches into another object's data more than its
  own. Move the method onto the data it envies.
- **Data clumps** - the same few fields or parameters keep travelling together.
  Bundle them into one type and pass that.
- **Primitive obsession** - a primitive or string stands in for a domain concept
  that deserves its own small type.
- **Repeated switches** - the same switch or if-cascade on the same type recurs.
  Replace it with polymorphism, or one map both sites share.
- **Shotgun surgery** - one logical change forces scattered edits across many
  files. Gather what changes together into one module.
- **Divergent change** - one file is edited for several unrelated reasons. Split
  it so each module changes for one reason.
- **Speculative generality** - abstraction, parameters, or hooks exist for needs
  the spec does not have. Delete them; inline until a real need shows.
- **Message chains** - long `a.b().c().d()` navigation the caller should not
  depend on. Hide the walk behind one method on the first object.
- **Middle man** - a class or function mostly just delegates onward. Cut it and
  call the real target direct.
- **Refused bequest** - a subclass or implementer ignores or overrides most of
  what it inherits. Drop the inheritance and use composition.
