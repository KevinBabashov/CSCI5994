# Design Notes

The runnable code follows a small SOLID-oriented layout:

- Single responsibility: synthetic data generation, abundance parsing, pipeline rendering, model
  training, reporting, and dashboard display live in separate modules.
- Open/closed: new profilers can be added by introducing a parser/renderer module without rewriting
  the dashboard or synthetic data generator.
- Liskov substitution: generated tables use stable tabular contracts, so synthetic and real Emu-style
  outputs can be consumed through the same analysis functions.
- Interface segregation: command-line tasks are small and focused instead of exposing one large
  all-purpose pipeline function.
- Dependency inversion: the dashboard depends on analysis functions and config files, not on direct
  shell execution or hard-coded server paths.

Practical rule: when a notebook cell becomes a repeatable workflow step, move it into
`src/minnelove_emu` and call that Python function from the notebook.

